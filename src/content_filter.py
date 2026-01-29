from bs4 import BeautifulSoup
import re
from openai import OpenAI
import json
import lxml

with open("config/credentials/api_keys.json","r") as f:
    credentials_file = json.load(f)

import re
from bs4 import BeautifulSoup

def extract_content_from_html(list_emails: list[dict]) -> list[str]:
    
    list_emails_clean = []

    for email in list_emails:
        html_content = email["content"]
        sender = email["sender"]
        
        # 'lxml' é o parser mais robusto para newsletters
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove elementos invisíveis
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Captura Manchetes (h1, h2, h3) e Parágrafos (p)
        elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
        
        cleaned_paragraphs = []
        for element in elements:
            text = element.get_text(" ", strip=True)
            
            # Filtros de relevância
            if not text or len(text) < 5:
                continue

            # 1. Remove apenas os Links (URLs e links entre parênteses)
            text = re.sub(r'\(https?://\S+\)|https?://\S+', '', text)
            
            # 2. Limpa espaços duplos resultantes da remoção de links
            text = re.sub(r'\s+', ' ', text).strip()

            if text:
                # Mantém a estrutura de tópicos para ajudar a IA no próximo passo
                if element.name in ['h1', 'h2', 'h3']:
                    cleaned_paragraphs.append(f"\n--- TÓPICO: {text} ---")
                else:
                    cleaned_paragraphs.append(text)

        header = f"FONTE: {sender}\n"
        full_body = "\n".join(cleaned_paragraphs)
        list_emails_clean.append(header + full_body)
            
    return list_emails_clean

def filter_news(formatted_text:str,credentials_file) -> str:
    client = OpenAI(
    api_key=credentials_file["openAI"],
)
    response = client.responses.create(
        model="gpt-5-nano",
        reasoning={"effort": "low"},
        input=[
            {
                "role": "system",
                "content": (
                    "Você é um Agente de Curadoria de Conteúdo especializado em newsletters sobre notícias e tecnologia.\n"
                    "Seu objetivo é separar notícias reais de conteúdo irrelevante.\n\n"
                    "DEFINIÇÕES:\n"
                    "- NOTÍCIA: Informação factual sobre tecnologia, ciência, negócios, economia ou acontecimentos do mundo.\n"
                    "- RUÍDO: Propaganda, anúncio patrocinado, venda de curso, depoimento pessoal, "
                    "chamada comercial, link de afiliado ou aviso administrativo.\n\n"
                    "REGRAS:\n"
                    "1. O texto de entrada contém vários blocos separados por \n\n--- TÓPICO:"
                    "2. Analise cada bloco de forma independente.\n"
                    "3. Se o bloco for RUÍDO, descarte-o completamente.\n"
                    "4. Se o bloco for NOTÍCIA:\n"
                    "   - Mantenha apenas o conteúdo informativo.\n"
                    "   - Remova chamadas comerciais, CTAs e referências visuais.\n"
                    "   - Não adicione informações novas.\n"
                    "5. Preserve o texto em português.\n"
                    "6. Não explique decisões nem adicione comentários.\n\n"
                    "FORMATO DE SAÍDA:\n"
                    "- Antes do conteúdo,informe o responsável pela newsletter, identificando seu nome através do mandante"
                    "- Retorne somente os blocos classificados como NOTÍCIA.\n"
                    "- O formato da saída deve ter um separados claro entre as notícias:\n"
                    "Fonte: [Nome do Remetente]\n"
                    "SEPARADOR"
                    "[Conteúdo informativo 1]\n"
                    "SEPARADOR"
                    "[Conteúdo informativo 2]\n"
                    "SEPARADOR"
                    "- Não inclua texto antes ou depois do conteúdo final.\n\n"
                )
            },
            {
                "role": "user",
                "content": f"TEXTO PARA ANÁLISE:\n{formatted_text}"
            }
        ]
    )
    return response.output_text

