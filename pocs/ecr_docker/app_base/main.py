import requests
import json
from random import choice
from config import API_KEY, MODO_LOCAL, HABILITAR_LOGIN
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from notificacoes_local import init_db, salvar_notificacao, listar_notificacoes
import openai
import markdown


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="chave-ultrasecreta")  # Trocar para prod
templates = Jinja2Templates(directory="templates")

openai.api_key = API_KEY

# Carrega mock se em modo local
if MODO_LOCAL:
    with open("mock_data.json", "r", encoding="utf-8") as f:
        MOCK = json.load(f)


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/")
async def homepage(request: Request):
    session = request.session

    if HABILITAR_LOGIN and not session.get("usuario_logado"):
        return RedirectResponse("/login")

    return templates.TemplateResponse("index.html", {"request": request, "session": session})

@app.get("/api/sorte")
async def gerar_sorte(request: Request):
    session = request.session

    if "sorte_do_dia" in session:
        return JSONResponse({"sorte": session["sorte_do_dia"]})

    if MODO_LOCAL:
        session["sorte_do_dia"] = MOCK["sorte_do_dia"]
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.1-mini",
                timeout=15,
                messages=[
                    {"role": "system", "content": "Você é um gerador de frases motivacionais estilo Orkut"},
                    {"role": "user", "content": "Me dê uma sorte do dia criativa, curta e positiva, como as do antigo Orkut. Retorne, Sorte do dia: <frase motivacional e emojis>"}
                ]
            )
            session["sorte_do_dia"] = response.choices[0].message['content'].strip()
        except Exception as e:
            session["sorte_do_dia"] = "✨ Hoje é um bom dia para recomeçar, com calma e propósito."

    return JSONResponse({"sorte": session["sorte_do_dia"]})

@app.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_submit(request: Request, usuario: str = Form(...), senha: str = Form(...)):
    session = request.session

    # Simples login didático
    if usuario == "admin" and senha == "123":
        session["usuario_logado"] = usuario
        return RedirectResponse("/", status_code=303)
    else:
        return RedirectResponse("/login", status_code=303)


@app.post("/gerar")
async def gerar_pergunta(request: Request):
    session = request.session

    if MODO_LOCAL:
        pergunta_mock = choice(MOCK["perguntas"])
        session["pergunta"] = pergunta_mock["pergunta"]
        session["resposta_correta"] = pergunta_mock["resposta_correta"]
        session["explicacao"] = pergunta_mock["explicacao"]
        session["resultado"] = ""
        session["acertou"] = None
    else:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente de quiz e especialista em AWS - Certificação SAA-C03."},
                {"role": "user", "content": "Por favor, me forneça uma pergunta de Verdadeiro ou Falso sobre AWS focado na certificação Solutions Architect Associate SAA-C03. Responda apenas com a pergunta."}
            ]
        )
        session["pergunta"] = response.choices[0].message['content']
        session["resposta_correta"] = ""
        session["explicacao"] = ""
        session["resultado"] = ""
        session["acertou"] = None

    return RedirectResponse("/", status_code=303)


@app.post("/responder")
async def responder(request: Request, resposta: str = Form(...)):
    session = request.session
    pergunta = session.get("pergunta", "")

    if not MODO_LOCAL:
        resposta_openai = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente de quiz e especialista em AWS - Certificação SAA-C03."},
                {"role": "user", "content": f"Qual é a resposta correta (Verdadeiro ou Falso) para a pergunta: '{pergunta}'? Responda apenas com 'Verdadeiro' ou 'Falso'."}
            ]
        )
        session["resposta_correta"] = resposta_openai.choices[0].message['content'].strip()

    # Lógica comum para acerto/erro
    if resposta.lower() == session["resposta_correta"].lower():
        session["resultado"] = "✅ Parabéns! Você acertou a resposta. 🎉"
        session["acertou"] = True
    else:
        session["resultado"] = "❌ Ops! Sua resposta está incorreta."
        session["acertou"] = False

    if not MODO_LOCAL:
        explicacao = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente de quiz e especialista em AWS - Certificação SAA-C03."},
                {"role": "user", "content": f"Explique a resposta {session['acertou'] and 'Correta' or 'Incorreta'} para a pergunta: '{pergunta}'. Retorne apenas a explicação detalhada até 200 palavras pode trazer formatação html dando enfase com negrito em palavras chave, não sugira ajuda ou mais detalhes apenas a explicação."}
            ]
        )
        session["explicacao"] = markdown.markdown(explicacao.choices[0].message['content'])

    return RedirectResponse("/", status_code=303)


@app.get("/notificacoes")
async def notificacoes():
    mensagens = await listar_notificacoes()
    return {"qtd": len(mensagens), "mensagens": mensagens}


@app.post("/sns-webhook")
async def receber_sns(payload: Request):
    data = await payload.json()

    if data.get("Type") == "SubscriptionConfirmation":
        token_url = data["SubscribeURL"]
        requests.get(token_url)

    elif data.get("Type") == "Notification":
        mensagem = data["Message"]
        print(f"🔔 SNS: {mensagem}")
        await salvar_notificacao(mensagem)

    return {"status": "ok"}

