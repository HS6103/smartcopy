import fire
from gpt_writer import process_news_story

def main():
    fire.Fire(process_news_story)

if __name__ == '__main__':
    main()

