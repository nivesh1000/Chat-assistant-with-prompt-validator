from class_implementation import Response

print('''Hello! 👋\nI'm here to assist you with your queries related to Petofy. You can ask me anything, and I'll do my best to help.\nTo end your session at any time, simply type "exit".\nHow can I assist you today?''')
user_input=""
while(user_input!="exit"):
    user_input = input("Query: ")
    if(user_input=="exit"):
        break
    Response(user_input)