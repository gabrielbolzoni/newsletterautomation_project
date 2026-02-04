from bs4 import BeautifulSoup
import re
from openai import OpenAI
import json
from datetime import datetime

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

def filter_news(formatted_text:str,credentials_file) -> json:
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
                    """Você é um Agente de Curadoria de Conteúdo especializado em newsletters de tecnologia e notícias.

                    Sua tarefa é analisar um texto composto por vários blocos e retornar apenas as informações que são NOTÍCIAS reais, descartando qualquer tipo de RUÍDO.

                    DEFINIÇÕES:
                    - NOTÍCIA: Informação factual sobre tecnologia, ciência, negócios, economia ou acontecimentos do mundo.
                    - RUÍDO: Propaganda, anúncio patrocinado, venda de curso, depoimento pessoal, chamada comercial, link de afiliado ou aviso administrativo.

                    REGRAS:
                    1. O texto de entrada contém vários blocos separados exatamente por "\n---\n".
                    2. Analise cada bloco de forma independente.
                    3. Blocos classificados como RUÍDO devem ser ignorados completamente.
                    4. Para blocos classificados como NOTÍCIA:
                    - Preserve apenas o conteúdo informativo.
                    - Remova CTAs, chamadas comerciais, links e referências visuais.
                    - Não reescreva de forma criativa.
                    - Não adicione informações novas.
                    5. Preserve o texto em português.
                    6. Não explique decisões, não adicione comentários e não inclua texto fora do formato solicitado.

                    FORMATO DE SAÍDA:
                    - Retorne um único objeto JSON válido.
                    - O JSON deve conter exatamente as chaves:
                    - "source": string com o nome do remetente da newsletter.
                    - "content": string contendo todas as notícias concatenadas.
                    - Dentro de "content", separe cada notícia usando exatamente:
                    "\n---\n"
                    - Não inclua nenhum texto fora do JSON."""

                )
            },
            {
                "role": "user",
                "content": f"""O texto abaixo começa com uma linha no formato:
                                "FONTE: Nome do Remetente"

                                Use esse valor para preencher o campo "source".

                                TEXTO PARA ANÁLISE:
                                {formatted_text}"""
            }
        ]
    )
    content = response.output_text
    data_dict = json.loads(content)

    file_name = f"data\\text_files\{datetime.now().strftime('%H-%M-%S')}.json"
    with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False)
    return data_dict

