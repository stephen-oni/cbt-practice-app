import fitz  # just likePyMuPDF
import streamlit as st
import re
import random

st.set_page_config(page_title="CBT Practice", page_icon="💻", layout="centered")

@st.cache_data
def parse_pdf_with_images(uploaded_file_bytes, answer_mode):
    doc = fitz.open(stream=uploaded_file_bytes, filetype="pdf")
    questions = []
    answers_dict = {}
    current_q = None

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text blocks into txt
        text_blocks = page.get_text("blocks")
        
        # Extract images cleanly
        images = []
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Exclude tiny icons or logos to not parse wrong images
            if len(image_bytes) > 5000:
                rects = page.get_image_rects(xref)
                if rects:
                    for rect in rects:
                        images.append({
                            "y0": rect.y0,
                            "bytes": image_bytes,
                            "type": "image"
                        })
        
        # Format text blocks
        blocks = []
        for b in text_blocks:
            if b[6] == 0:  # block_type 0 is text
                blocks.append({
                    "y0": b[1],
                    "text": b[4],
                    "type": "text"
                })
        
        # Combine and sort top to bottom
        all_blocks = blocks + images
        all_blocks.sort(key=lambda b: b["y0"])
        
        # Parse the blocks
        for block in all_blocks:
            if block["type"] == "text":
                lines = block["text"].split("\n")
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Ignore PDF headers/footers if any still in better mode
                    if "The safer, easier way" in line or "KillTest" in line or re.match(r"^\d+/\d+$", line):
                        continue
                    
                    # answer key dectection for 'End of Document' mode
                    if answer_mode == "End of Document":
                        # Strip prefixes like "Answer:" or "Answers:"
                        test_line = re.sub(r"^(answer|answers|answer key|key)s?\s*[:\-]?\s*", "", line, flags=re.IGNORECASE)
                        # Look for mappings like "1. A", "2: B,C", "3 AB"
                        pairs = re.findall(r"\b(\d+)\s*[\.\:\-]?\s*([A-F][A-F\,\s]*)\b", test_line, flags=re.IGNORECASE)
                        
                        if pairs:
                            # Verify this line is PURELY an answer mapping
                            residual = re.sub(r"\b\d+\s*[\.\:\-]?\s*[A-F][A-F\,\s]*\b", "", test_line, flags=re.IGNORECASE)
                            residual = re.sub(r"[^a-zA-Z0-9]", "", residual) # Remove punctuation/spaces
                            
                            if not residual: # If nothing alphanumeric is left, it's a guaranteed answer key line!
                                for num, ans in pairs:
                                    # Clean up the answer
                                    ans_clean = "".join(c for c in ans.upper() if c in "ABCDEF")
                                    if ans_clean:
                                        answers_dict[str(num)] = ans_clean

                    # question detection
                    q_match = re.match(r"^(\d+)\.(?!\d)", line)
                    if q_match:
                        # Save the previous question before starting a new one
                        if current_q and current_q.get("options"):
                            if answer_mode == "Inline" and current_q.get("answer"):
                                questions.append(current_q)
                            elif answer_mode == "End of Document":
                                questions.append(current_q)
                                
                        current_q = {
                            "id": str(q_match.group(1)),
                            "question": line,
                            "options": [],
                            "answer": "",
                            "images": []
                        }
                    
                    # option detection
                    elif re.match(r"^[A-Fa-f][\.\)]", line) and current_q is not None:
                        current_q["options"].append(line)
                    
                    # inline answer detection
                    elif answer_mode == "Inline" and line.lower().startswith("answer:") and current_q is not None:
                        current_q["answer"] = line.split(":", 1)[-1].strip().upper()
                    
                    # multiple choice answer detection
                    elif current_q is not None:
                        if not current_q["answer"]:
                            if current_q["options"]:
                                current_q["options"][-1] += " " + line
                            else:
                                current_q["question"] += "\n" + line
                                
            elif block["type"] == "image":
                if current_q is not None:
                    current_q["images"].append(block["bytes"])

    # Append the very last question
    if current_q and current_q.get("options"):
        if answer_mode == "Inline" and current_q.get("answer"):
            questions.append(current_q)
        elif answer_mode == "End of Document":
            questions.append(current_q)

    # map answers to questions for 'End of Document' mode
    if answer_mode == "End of Document":
        final_questions = []
        for q in questions:
            q_id = q.get("id")
            if q_id in answers_dict:
                q["answer"] = answers_dict[q_id]
                final_questions.append(q)
        questions = final_questions

    return questions




# the UI part of the app
st.title("💻 Local CBT Practice")
st.write("Upload your PDF below")
st.write("built by github.com/stephen-oni")

st.markdown("## ⚙️ Settings")
answer_mode = st.radio(
    "How are the answers formatted in your PDF?", 
    ["Inline", "End of Document"],
    captions=["Answers are placed immediately below each question (e.g. Answer: A)", "An Answer Key list is located at the very end of the document"]
)

uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

if uploaded_file is not None:
    # Use a combined cache key so switching modes triggers a re-parse
    cache_key = f"{uploaded_file.name}_{answer_mode}"
    
    if "file_name" not in st.session_state or st.session_state.file_name != cache_key:
        with st.spinner("Parsing text, diagrams, and answer keys..."):
            file_bytes = uploaded_file.read()
            st.session_state.questions = parse_pdf_with_images(file_bytes, answer_mode)
            st.session_state.file_name = cache_key
            random.shuffle(st.session_state.questions)
            st.session_state.current_q = 0
            st.session_state.submitted = False

    questions = st.session_state.questions

    if questions:
        idx = st.session_state.current_q
        q = questions[idx]

        st.subheader(f"Question {idx + 1} of {len(questions)}")
        st.write(f"*(Original Q-Num: {q['id']})*")
        st.write(f"**{q['question']}**")

        if q.get("images"):
            for img_bytes in q["images"]:
                st.image(img_bytes, use_container_width=True)

        is_multiple = len(q["answer"]) > 1

        opt_key = f"shuffled_opt_{idx}"
        if opt_key not in st.session_state:
            shuffled_opts = q["options"].copy()
            random.shuffle(shuffled_opts)
            st.session_state[opt_key] = shuffled_opts
        else:
            shuffled_opts = st.session_state[opt_key]

        if is_multiple:
            st.caption("*(Multiple Choice Question — Select all that apply)*")
            selected = st.multiselect("Choose your options:", shuffled_opts, key=f"choice_{idx}")
        else:
            selected = st.radio("Choose your option:", shuffled_opts, key=f"choice_{idx}", index=None)

        if st.button("Submit Answer"):
            st.session_state.submitted = True
            
            if is_multiple:
                selected_letters = "".join(sorted([s.split(".")[0].strip().upper() for s in selected]))
                correct_letters = "".join(sorted(q["answer"]))
                
                if selected_letters == correct_letters:
                    st.success(f"Correct! The answer is: {q['answer']}")
                else:
                    st.error(f"Incorrect. You chose {selected_letters}, but the correct answer is: {q['answer']}")
            else:
                selected_letter = selected.split(".")[0].strip().upper() if selected else ""
                if selected_letter == q["answer"]:
                    st.success(f"Correct! The answer is: {q['answer']}")
                else:
                    st.error(f"Incorrect. The correct answer is: {q['answer']}")

        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Next Question ➡") and idx < len(questions) - 1:
                st.session_state.current_q += 1
                st.session_state.submitted = False
                st.rerun()
        with col2:
            if st.button("⬅ Previous Question") and idx > 0:
                st.session_state.current_q -= 1
                st.session_state.submitted = False
                st.rerun()
    else:
        st.warning(f"No valid questions/answers found for '{answer_mode}' mode. Please check the PDF layout or try switching the Answer Format setting.")