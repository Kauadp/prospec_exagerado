import requests
import os
import json
import streamlit as st
import sys

def enviar_para_autentique(
    caminho_pdf,
    nome_documento,
    nome_signatario,
    email_signatario,
    token_autentique=None
):
    """
    Envia um documento para a API v3 da Autentique para assinatura digital.
    
    Args:
        caminho_pdf: Caminho do arquivo PDF a ser enviado
        nome_documento: Nome do documento
        nome_signatario: Nome do signatário
        email_signatario: Email do signatário
        token_autentique: Token da Autentique (se None, lança erro)
    
    Returns:
        Resposta JSON da API Autentique
    """
    
    if not token_autentique:
        raise ValueError(
            "Token da Autentique não fornecido.\n"
            "Passe token_autentique como parâmetro ou configure AUTENTIQUE_TOKEN no .env"
        )

    url = "https://api.autentique.com.br/v2/graphql"

    headers = {
        "Authorization": f"Bearer {token_autentique}",
    }

    query = """
    mutation RealizarDisparo($documento: DocumentInput!, $signatarios: [SignerInput!], $arquivo: Upload!) {
      createDocument(document: $documento, signers: $signatarios, file: $arquivo) {
        id
        name
        signatures {
          public_id
          name
          email
          link {
            short_link
          }
        }
      }
    }
    """

    operations = {
        "query": query,
        "variables": {
            "documento": {
                "name": nome_documento
            },
            "signatarios": [
                {
                    "name": "VICTOR DE CASTRO PEREIRA",
                    "email": "gabrielly.concecio@alfaiatariadeideias.com.br",
                    "action": "SIGN"
                },
                {
                    "name": nome_signatario,
                    "email": email_signatario,
                    "action": "SIGN"
                }
            ],
            "arquivo": None  
        }
    }

    map_ = {
        "file": ["variables.arquivo"]
    }

    try:
        with open(caminho_pdf, "rb") as f:
            files = {
                "operations": (None, json.dumps(operations), "application/json"),
                "map": (None, json.dumps(map_), "application/json"),
                "file": (nome_documento + ".pdf", f, "application/pdf")
            }

            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response.json()
            
    except Exception as e:
        return {"errors": [{"message": f"Erro na conexão de transporte HTTP: {str(e)}"}]}