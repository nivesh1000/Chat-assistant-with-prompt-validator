from enum import Enum
from class_implementation import Response
import re
from test import UserModel, ValidationError

class ModerationCategory(Enum):
    CATEGORY1 = "category1"
    CATEGORY2 = "category2"
    CATEGORY3 = "category3"
    REVIEW_RECOMMENDED = "review_recommended"

def main() -> None:
    user_query = input("Query: ")
    try:
        query = UserModel(user_query=user_query)
        # cur_query = Response(query)
        # moder_result = cur_query.moderator_setup

        # if (moder_result.get('classification').get(ModerationCategory.CATEGORY3.value).get("score") > 0.5 or
        #     moder_result.get('classification').get(ModerationCategory.CATEGORY2.value).get("score") > 0.5 or
        #     moder_result.get('classification').get(ModerationCategory.CATEGORY1.value).get("score") > 0.5 or
        #     moder_result.get('classification').get(ModerationCategory.REVIEW_RECOMMENDED.value) == True):
        #     print("Response: I can't answer questions like that. Please ask another question.")
        # else:
        #     print("Response: ", re.sub(r'\[doc\d+\]', '', cur_query.chat_completion_setup))

        # del cur_query
        
    except ValidationError as e:
        print(f"Value error: {e.errors()[0]['msg']}")    

if __name__ == "__main__":
    main()