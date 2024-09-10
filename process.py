import os
import ollama

# 질문 분석용 (ollama 사용)
def analyze_request(question):
    prompt = f"다음 요청을 분석하고, 해당 작업이 데이터 필터링인지, 아니면 요약, 주제 유추와 같은 작업인지 판단하십시오. 요청: {question}"
    response = ollama.chat(
        model='llama3.1',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']

# 자연어 응답용 (ollama 사용)
def ai_answer_gen(question, context=""):
    prompt = f"다음 데이터를 기반으로 주제를 유추하십시오.\n질문: {question}\n데이터: {context}\n답변:"
    response = ollama.chat(
        model='llama3.1',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['message']['content']

# steam.txt 파일 파싱
def parser(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line:
                score, content = line.split("\t", 1)
                data.append({"score": score, "content": content})
    return data

# 데이터 필터링용 (긍부정 데이터 구분)
def filter_data(data, condition):
    filtered_data = []
    for entry in data:
        score = entry["score"]
        content = entry["content"]

        if "긍정" in condition and score == "1":
            filtered_data.append(content)
        elif "부정" in condition and score == "0":
            filtered_data.append(content)
        elif condition in content:
            filtered_data.append(content)
    
    return filtered_data

# 사용자의 요청을 처리하는 함수
def handle_request(request, file_path):

    task = analyze_request(request)

    data = parser(file_path)

    if "요약" in task or "주제 유추" in task:
        context = "\n".join([entry["content"] for entry in data])
        model_response = ai_answer_gen(request, context)
        return {"response": model_response}

    elif "필터" in task:
        filtered_data = filter_data(data, request)
        if filtered_data:
            return {"filtered_data": filtered_data}
        else:
            return {"filtered_data": ["관련 데이터가 없습니다."]}

    else:
        return {"response": "적절한 작업을 수행할 수 없습니다."}

# 메인 함수
if __name__ == "__main__":

    user_input = input("사용자 입력: ")
    steam_txt_path = os.path.join(os.getcwd(), "data", "steam.txt")
    
    result = handle_request(user_input, steam_txt_path)
    
    if "filtered_data" in result:
        print("필터링된 데이터:", "\n".join(result["filtered_data"]))
    elif "response" in result:
        print("Ollama 응답:", result["response"])
