import requests
import time
import logging
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

SERVER_URL = "http://server:8080"
REQUEST_INTERVAL = 5 

class HTTPClient:
    
    def __init__(self, server_url: str, interval: int):
        self.server_url = server_url
        self.interval = interval
        self.successful_requests = 0
        self.failed_requests = 0
    
    def make_request(self, endpoint: str = "/") -> dict:
        
        url = f"{self.server_url}{endpoint}"
        try:
            logger.info(f"Enviando requisição para {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            self.successful_requests += 1
            data = response.json()
            
            logger.info(f"✓ Resposta recebida (Status: {response.status_code})")
            logger.info(f"  Mensagem: {data.get('message', 'N/A')}")
            logger.info(f"  Timestamp: {data.get('timestamp', 'N/A')}")
            logger.info(f"  Request #: {data.get('request_number', 'N/A')}")
            
            return data
            
        except requests.exceptions.ConnectionError as e:
            self.failed_requests += 1
            logger.error(f"✗ Erro de conexão: Não foi possível conectar ao servidor")
            return {"error": "connection_error", "details": str(e)}
            
        except requests.exceptions.Timeout as e:
            self.failed_requests += 1
            logger.error(f"✗ Timeout: Servidor não respondeu a tempo")
            return {"error": "timeout", "details": str(e)}
            
        except requests.exceptions.RequestException as e:
            self.failed_requests += 1
            logger.error(f"✗ Erro na requisição: {e}")
            return {"error": "request_error", "details": str(e)}
    
    def check_health(self) -> bool:
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_stats(self) -> dict:
        try:
            response = requests.get(f"{self.server_url}/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {}
    
    def print_statistics(self):
        total = self.successful_requests + self.failed_requests
        success_rate = (self.successful_requests / total * 100) if total > 0 else 0
        
        logger.info("=" * 60)
        logger.info("ESTATÍSTICAS DO CLIENTE")
        logger.info(f"  Total de requisições: {total}")
        logger.info(f"  Sucessos: {self.successful_requests}")
        logger.info(f"  Falhas: {self.failed_requests}")
        logger.info(f"  Taxa de sucesso: {success_rate:.2f}%")
        logger.info("=" * 60)
    
    def run(self):
        logger.info("=" * 60)
        logger.info("Cliente HTTP iniciado")
        logger.info(f"Servidor alvo: {self.server_url}")
        logger.info(f"Intervalo entre requisições: {self.interval} segundos")
        logger.info("=" * 60)
        
        logger.info("Aguardando servidor ficar disponível...")
        max_retries = 30
        for i in range(max_retries):
            if self.check_health():
                logger.info("✓ Servidor disponível!")
                break
            logger.info(f"Tentativa {i+1}/{max_retries}: Servidor ainda não disponível")
            time.sleep(2)
        else:
            logger.error("✗ Servidor não ficou disponível após múltiplas tentativas")
            return
        
        request_count = 0
        try:
            while True:
                request_count += 1
                logger.info(f"\n--- Requisição #{request_count} ---")
                
                self.make_request("/")
                
                if request_count % 5 == 0:
                    logger.info("\n--- Consultando estatísticas do servidor ---")
                    stats = self.get_stats()
                    if stats:
                        logger.info(f"Estatísticas do servidor: {stats}")
                    
                    self.print_statistics()
                
                logger.info(f"\nAguardando {self.interval} segundos...")
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("\n\nCliente interrompido pelo usuário")
            self.print_statistics()
        except Exception as e:
            logger.error(f"\nErro inesperado: {e}")
            self.print_statistics()


if __name__ == '__main__':
    client = HTTPClient(SERVER_URL, REQUEST_INTERVAL)
    client.run()
