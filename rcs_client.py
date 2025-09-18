import httpx
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class RCSAPIClient:
    def __init__(self):
        self.base_url = os.getenv("RCS_API_BASE_URL", "https://pointer-rcs-api-node.pontaltech.com.br")
        self.token = os.getenv("RCS_API_TOKEN")
        self.simulation_mode = os.getenv("SIMULATION_MODE", "False").lower() == "true"

        if not self.token and not self.simulation_mode:
            raise ValueError("RCS_API_TOKEN não configurado no arquivo .env")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Faz requisição para a API RCS"""

        # Modo simulação para testes
        if self.simulation_mode:
            logger.info(f"MODO SIMULAÇÃO - Endpoint: {endpoint}")
            logger.info(f"MODO SIMULAÇÃO - Dados: {data}")
            return {
                "success": True,
                "message_id": f"sim_{hash(str(data)) % 10000}",
                "status": "sent",
                "simulation": True
            }

        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                logger.info(f"Enviando requisição para {url}")
                logger.debug(f"Dados: {data}")

                response = await client.post(url, json=data, headers=self.headers)
                response.raise_for_status()

                result = response.json()
                logger.info(f"Resposta da API: {result}")
                return result

            except httpx.HTTPStatusError as e:
                logger.error(f"Erro HTTP {e.response.status_code}: {e.response.text}")
                raise Exception(f"Erro na API RCS: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                logger.error(f"Erro de conexão: {str(e)}")
                raise Exception(f"Erro de conexão com API RCS: {str(e)}")
            except Exception as e:
                logger.error(f"Erro inesperado: {str(e)}")
                raise Exception(f"Erro inesperado: {str(e)}")

    async def send_basic_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Envia mensagem RCS Basic"""
        return await self._make_request("/api/v3/basic", data)

    async def send_single_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Envia mensagem RCS Single"""
        return await self._make_request("/api/v3/single", data)

    async def send_webhook_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Envia mensagem RCS Conversacional (webhook)"""
        return await self._make_request("/api/v3/webhook", data)

    async def send_template_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Envia mensagem RCS Conversacional (template)"""
        return await self._make_request("/api/v3/template", data)

    async def create_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria template RCS"""
        return await self._make_request("/api/v3/templates", data)

    def validate_phone_number(self, phone: str) -> str:
        """Valida e formata número de telefone"""
        # Remove caracteres não numéricos
        clean_phone = ''.join(filter(str.isdigit, phone))

        # Adiciona código do país se necessário (Brasil = 55)
        if len(clean_phone) == 11 and clean_phone.startswith('0'):
            clean_phone = '55' + clean_phone[1:]
        elif len(clean_phone) == 10:
            clean_phone = '55' + clean_phone
        elif len(clean_phone) == 11 and not clean_phone.startswith('55'):
            clean_phone = '55' + clean_phone

        return clean_phone

    async def get_templates(self) -> Dict[str, Any]:
        """Busca templates disponíveis na plataforma"""
        if self.simulation_mode:
            logger.info("MODO SIMULAÇÃO - Listando templates")
            return {
                "templates": [
                    {
                        "id": "template_exemplo_1",
                        "name": "Template de Boas Vindas",
                        "type": "richCard",
                        "created_at": "2025-07-31T10:00:00Z"
                    },
                    {
                        "id": "teste_operadoras",
                        "name": "Teste Operadoras",
                        "type": "text",
                        "created_at": "2025-07-30T15:30:00Z"
                    }
                ]
            }

        # Possíveis endpoints para buscar templates
        endpoints_to_try = [
            "/api/v3/templates",
            "/api/templates",
            "/templates",
            "/api/v3/template/list",
            "/api/template/list",
            "/api/v3/account/templates"
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint in endpoints_to_try:
                try:
                    url = f"{self.base_url}{endpoint}"
                    logger.info(f"Tentando buscar templates em: {endpoint}")

                    # Tenta GET primeiro
                    response = await client.get(url, headers=self.headers)

                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Templates encontrados via GET {endpoint}: {result}")
                        return result

                    # Se GET não funcionar, tenta POST
                    if response.status_code in [404, 405]:
                        post_response = await client.post(url, headers=self.headers, json={})
                        if post_response.status_code == 200:
                            result = post_response.json()
                            logger.info(f"Templates encontrados via POST {endpoint}: {result}")
                            return result

                except Exception as e:
                    logger.debug(f"Erro ao tentar {endpoint}: {str(e)}")
                    continue

        # Se não encontrou nenhum endpoint, retorna erro informativo
        raise Exception("Não foi possível encontrar endpoint para listar templates. Contate apoio.ca@pontaltech.com.br")

    async def get_template_by_id(self, template_id: str) -> Dict[str, Any]:
        """Busca um template específico por ID"""
        if self.simulation_mode:
            logger.info(f"MODO SIMULAÇÃO - Buscando template: {template_id}")
            return {
                "id": template_id,
                "name": f"Template {template_id}",
                "type": "richCard",
                "content": {
                    "title": "Template de exemplo",
                    "description": "Este é um template de exemplo"
                },
                "variables": ["nome", "empresa", "produto"]
            }

        endpoints_to_try = [
            f"/api/v3/templates/{template_id}",
            f"/api/templates/{template_id}",
            f"/templates/{template_id}"
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint in endpoints_to_try:
                try:
                    url = f"{self.base_url}{endpoint}"
                    logger.info(f"Buscando template {template_id} em: {endpoint}")

                    response = await client.get(url, headers=self.headers)

                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Template {template_id} encontrado: {result}")
                        return result

                except Exception as e:
                    logger.debug(f"Erro ao buscar template em {endpoint}: {str(e)}")
                    continue

        raise Exception(f"Template {template_id} não encontrado na plataforma")
        """Valida conteúdo do fallback SMS"""
        # Remove acentos e caracteres especiais
        import unicodedata
        normalized = unicodedata.normalize('NFD', content)
        ascii_content = normalized.encode('ascii', 'ignore').decode('ascii')

        # Limita a 160 caracteres
        return ascii_content[:160]