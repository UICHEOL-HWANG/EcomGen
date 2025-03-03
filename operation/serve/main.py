from router.generate_model import create_description_pipeline, generate_description
from router.clean_text import clean_text

def main():
    pipe = create_description_pipeline("C:/Users/user/Desktop/EcomGen/model/Polyglot-ko-1.3b/merged_polyglot")
    desc = generate_description(pipe, product_name="저당 초코바")

    cleaned = clean_text(desc)

    result = clean_text(cleaned)

    return result


if __name__ == "__main__":
    print(main())