import pikepdf

def debug_pdf(pdf_path, password=None):
    print("function STARTED")
    print("[*] Attempting to open PDF...")

    try:
        if password:
            pdf = pikepdf.open(pdf_path, password=password)
        else:
            pdf = pikepdf.open(pdf_path)

        print("[+] PDF opened successfully.")
        print("[*] Is encrypted?", pdf.is_encrypted)

        print("\n=== ENCRYPTION INFO ===")
        print(pdf.encryption)

        print("\n=== RAW METADATA OBJECT ===")
        print(pdf.docinfo)   # This shows raw metadata dict

        if len(pdf.docinfo) == 0:
            print("[!] No metadata stored in the PDF.")
        else:
            print("\n=== METADATA FIELDS ===")
            for k, v in pdf.docinfo.items():
                print(f"{k}: {v}")

        pdf.close()

    except pikepdf._qpdf.PasswordError:
        print("❌ Wrong password.")
    except Exception as e:
        print("❌ Error:", e)

def main():
    print("SCRIPT STARTED")
    debug_pdf("Digits.pdf", "12354")

if __name__=="__main__":
    main()
