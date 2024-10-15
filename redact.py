import fitz  # PyMuPDF
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
import os

input_dir = 'to_redact/'
output_dir = 'redacted/'
files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")])

# Open all documents to be redacted
docs = []
for f in files:
        # Open the PDF
        docs.append(fitz.open(input_dir + f))
active_doc = 0

def save(doc_index):
    if os.path.isfile(f'{output_dir}{files[doc_index]}_redacted.pdf'):
        # Confirm save operation
        response = messagebox.askokcancel("Overwrite Confirmation", f"!!! WARNING !!!\nFile {output_dir}{files[doc_index]}_redacted.pdf already exists. Would you like to continue and overwrite the existing file?")
        if not response:
            print("User canceled save")
            return
    doc = docs[doc_index]
    # Save the new PDF with redactions
    doc.save(f'{output_dir}{files[doc_index]}_redacted.pdf')
    print(f'Saved {output_dir}{files[doc_index]}_redacted.pdf')

def save_current():
    global active_doc
    save(active_doc)

def save_all():
    for i in range(len(docs)):
        save(i)

def quit():
    print("!!! WARNING !!!\nRemember to delete your input documents that you are done with, or move your redacted output to a safe location.\nReloading the program and saving with the same documents as input will overwrite the output files.")
    for doc in docs:
        doc.close()
    root.destroy()

def get_selected_text():
    try:
        # Get the selected text
        selected_text = pdf_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        return selected_text
    except tk.TclError:
        # In case no text is selected
        print("No text selected.")

def show_pdf():
    global active_doc
    text_body = ""
    if len(files) ==  0:
        text_body += f"No PDF files found.\n\nPlease add the PDF files that you wish to redact into the input directory. \nOnce you perform some redactions and save, the redacted output PDF files will appear in the output directory.\n\nInput directory: {input_dir}\nOutput directory:{output_dir}\n\nTo redact text, simply highlight the text you wish to redact and then click one of the two redaction buttons at the bottom to redact the selected text from the current document or all loaded documents.\n\nThis text box displays one document at a time, and the two buttons at the bottom navigate between the loaded documents.\n\nWhen you are done and wish to save your redacted document, click one of the buttons to save just the current document or all of the loaded documents. \nBe careful and understand that you are saving only the redactions made during this session, i.e. when you reopen the program, the original uncensored document is loaded instead of making changes on any previously saved redacted documents. If you made redactions to a file and saved it in a previous session and want to add the already-redacted file, simply move that file from the output directory to the input directory (and probably remove the original input file to avoid confusion)\n\nDon't worry, when you are ready to save, you will be alerted if an output file of the same name already exists and asked to confirm the overwrite."
    else:
        # for i, doc in enumerate(docs):
        #     text_body += f"--- Document {i+1}: {files[i]} ---\n"
        #     for page_num in range(len(doc)):
        #         page = doc[page_num]
        #         text = page.get_text("text")  # Extract plain text from the page
        #         text_body += f"--- Text on Page {page_num + 1} ---\n"
        #         text_body += text
        text_body += f"--- Document {active_doc+1}: {files[active_doc]} ---\n"
        doc = docs[active_doc]
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")  # Extract plain text from the page
            text_body += f"--- Text on Page {page_num + 1} ---\n"
            text_body += text
    pdf_text.config(state=tk.NORMAL)
    pdf_text.delete("1.0", tk.END)
    pdf_text.insert(tk.END, text_body)
    pdf_text.config(state=tk.DISABLED)

# Function for redacting text from a document
def redact(text, doc_index):
    print(f'Redacting:\n{text} from doc {doc_index}')
    doc = docs[doc_index]
    for page in doc:
        # Search for text to redact
        text_instances = page.search_for(text)  # Replace with actual text

        # Redact the text by drawing an opaque rectangle over it and removing the original text
        for inst in text_instances:
            print("Redacting instance at {inst}")
            page.add_redact_annot(inst, fill=(0, 0, 0))  # Add redaction annotation (black fill)
            page.apply_redactions()  # Apply the redaction (removes the text beneath)

# Redacts from current doc
def redact_selection():
    global active_doc
    text = get_selected_text()
    redact(text, active_doc)
    show_pdf()

# Redacts from all docs
def redact_selection_all():
    text = get_selected_text()
    for i in range(len(docs)):
        redact(text, i)
    show_pdf()

def previous_doc():
    global active_doc
    if active_doc > 0:
        active_doc -= 1
        show_pdf()

def next_doc():
    global active_doc
    if active_doc < len(docs)-1:
        active_doc += 1
        show_pdf()

# tkinter time
root = tk.Tk()
root.title("PDF Redactor 3000 (Premium Subscription)")
root.geometry("800x600")

pdf_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=28)
pdf_text.config(state=tk.DISABLED)
pdf_text.pack(padx=10, pady=0)


btn_redact = tk.Button(root, text="Redact", command=redact_selection)
btn_redact.pack(side=tk.LEFT, padx=10, pady=10)

btn_redact_all = tk.Button(root, text="Redact All Docs", command=redact_selection_all)
btn_redact_all.pack(side=tk.LEFT, padx=10, pady=10)

btn_prev_doc = tk.Button(root, text="Prev Doc", command=previous_doc)
btn_prev_doc.pack(side=tk.LEFT, padx=10, pady=10)

btn_next_doc = tk.Button(root, text="Next Doc", command=next_doc)
btn_next_doc.pack(side=tk.LEFT, padx=10, pady=10)

btn_quit = tk.Button(root, text="Quit", command=quit)
btn_quit.pack(side=tk.RIGHT, padx=10, pady=10)

btn_save = tk.Button(root, text="Save All", command=save_all)
btn_save.pack(side=tk.RIGHT, padx=10, pady=10)

btn_save = tk.Button(root, text="Save", command=save_current)
btn_save.pack(side=tk.RIGHT, padx=10, pady=10)

# Start the Tkinter event loop
show_pdf()
root.mainloop()
