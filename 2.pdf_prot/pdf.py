import PyPDF2
import sys

def create_pass_protected_pdf(in_pdf,out_pdf,password):
    try:
        with open(in_pdf,'rb') as in_file:
            pdf_reader = PyPDF2.PdfReader(in_file)
            pdf_writer = PyPDF2.PdfWriter()

            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])
            
            pdf_writer.encrypt(password)

            with open(out_pdf,'wb') as out_file:
                pdf_writer.write(out_file)
            print("PDF is now Password Protected and saved as ",out_pdf)
    
    except FileNotFoundError:
        print("File does not Exist : ",{in_pdf})
    #except PyPDF2.utils.PdfReadError:
     #   print(f'The file {in_pdf} is not valid')
    except Exception as e:
        print('Error',e)

def main():
    if len(sys.argv) != 4:
        print("Usage: python pdf.py <input_pdf> <output_pdf> <password>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    password = sys.argv[3]

    create_pass_protected_pdf(input_pdf,output_pdf,password)

if __name__=="__main__":
    main()
