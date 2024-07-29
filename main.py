from enum import Enum
from class_implementation import Response
import re
import endpoint_validator

class ModerationCategory(Enum):
    CATEGORY1 = "category1"
    CATEGORY2 = "category2"
    CATEGORY3 = "category3"
    REVIEW_RECOMMENDED = "review_recommended"

def main() -> None:
    print('''Hello! 👋\nI'm here to assist you with your queries related to Petofy.
    You can ask me anything, and I'll do my best to help.
    To end your session at any time, simply type "exit".
    How can I assist you today?''')

    while True:
        user_input = input("Query: ")
        if user_input.lower() == "exit":
            break
    
        cur_query = Response(user_input)
        moder_result = cur_query.moderator_setup

        if (moder_result.get('classification').get(ModerationCategory.CATEGORY3.value).get("score") > 0.5 or
            moder_result.get('classification').get(ModerationCategory.CATEGORY2.value).get("score") > 0.5 or
            moder_result.get('classification').get(ModerationCategory.CATEGORY1.value).get("score") > 0.5 or
            moder_result.get('classification').get(ModerationCategory.REVIEW_RECOMMENDED.value) == True):
            print("Response: I can't answer questions like that. Please ask another question.")
        else:
            print("Response: ", re.sub(r'\[doc\d+\]', '', cur_query.chat_completion_setup))

        del cur_query

    print("Your session has ended. Thank you and goodbye! 👋")

if __name__ == "__main__":
    main()