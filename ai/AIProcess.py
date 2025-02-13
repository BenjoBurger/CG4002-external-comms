def ai_process(eval_to_ai_queue, ai_to_eval_queue):
    while True:
        msg = eval_to_ai_queue.get()
        if msg == "exit":
            break
        if msg == "ai":
            ai_to_eval_queue.put("ai")
        else:
            print("Invalid message received")