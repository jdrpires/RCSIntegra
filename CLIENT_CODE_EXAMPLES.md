# 💻 RCS Gateway - Exemplos de Código

Exemplos de integração com a API RCS Gateway em diferentes linguagens de programação.

## 🐍 Python

### Instalação
```bash
pip install requests
```

### Exemplo Básico
```python
import requests
import json

class RCSGatewayClient:
    def __init__(self, base_url, api_key, client_code):
        self.base_url = base_url
        self.api_key = api_key
        self.client_code = client_code
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def send_message(self, phone_numbers, content, message_type='basic', **kwargs):
        """Envia mensagem RCS"""
        payload = {
            'client_code': self.client_code,
            'message_type': message_type,
            'phone_numbers': phone_numbers,
            'content': content,
            **kwargs
        }
        
        response = requests.post(
            f'{self.base_url}/api/client/send-message',
            headers=self.headers,
            json=payload
        )
        
        return response.json()
    
    def get_messages(self, **filters):
        """Consulta mensagens"""
        params = {'client_code': self.client_code, **filters}
        
        response = requests.get(
            f'{self.base_url}/api/client/messages',
            headers=self.headers,
            params=params
        )
        
        return response.json()
    
    def get_stats(self):
        """Obtém estatísticas"""
        response = requests.get(
            f'{self.base_url}/api/client/stats',
            headers=self.headers
        )
        
        return response.json()

# Exemplo de uso
client = RCSGatewayClient(
    base_url='https://api.exemplo.com',
    api_key='sua_api_key_aqui',
    client_code='CLI_ABC123'
)

# Enviar mensagem de texto
result = client.send_message(
    phone_numbers=['5511999999999'],
    content={
        'text': {
            'message': 'Olá! Esta é uma mensagem de teste.'
        }
    },
    campaign_name='Teste Python'
)

print(f"Mensagem enviada: {result}")

# Enviar Rich Card
rich_card_result = client.send_message(
    phone_numbers=['5511999999999'],
    content={
        'richCard': {
            'title': 'Oferta Especial!',
            'description': 'Aproveite 50% de desconto',
            'fileUrl': 'https://exemplo.com/imagem.jpg',
            'suggestions': [
                {
                    'type': 'openUrl',
                    'title': 'Ver Produtos',
                    'value': 'https://loja.exemplo.com'
                }
            ]
        }
    },
    message_type='single'
)

# Consultar mensagens
messages = client.get_messages(status='delivered', limit=10)
print(f"Mensagens entregues: {len(messages)}")

# Obter estatísticas
stats = client.get_stats()
print(f"Total de mensagens: {stats['total_messages']}")
```

## ☕ Java

### Dependências (Maven)
```xml
<dependency>
    <groupId>com.squareup.okhttp3</groupId>
    <artifactId>okhttp</artifactId>
    <version>4.12.0</version>
</dependency>
<dependency>
    <groupId>com.google.code.gson</groupId>
    <artifactId>gson</artifactId>
    <version>2.10.1</version>
</dependency>
```

### Exemplo
```java
import okhttp3.*;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.IOException;
import java.util.List;
import java.util.Map;

public class RCSGatewayClient {
    private final String baseUrl;
    private final String apiKey;
    private final String clientCode;
    private final OkHttpClient client;
    private final Gson gson;
    
    public RCSGatewayClient(String baseUrl, String apiKey, String clientCode) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
        this.clientCode = clientCode;
        this.client = new OkHttpClient();
        this.gson = new Gson();
    }
    
    public String sendMessage(List<String> phoneNumbers, Map<String, Object> content, 
                             String messageType, String campaignName) throws IOException {
        
        JsonObject payload = new JsonObject();
        payload.addProperty("client_code", clientCode);
        payload.addProperty("message_type", messageType);
        payload.add("phone_numbers", gson.toJsonTree(phoneNumbers));
        payload.add("content", gson.toJsonTree(content));
        
        if (campaignName != null) {
            payload.addProperty("campaign_name", campaignName);
        }
        
        RequestBody body = RequestBody.create(
            payload.toString(),
            MediaType.get("application/json")
        );
        
        Request request = new Request.Builder()
            .url(baseUrl + "/api/client/send-message")
            .addHeader("X-API-Key", apiKey)
            .addHeader("Content-Type", "application/json")
            .post(body)
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            return response.body().string();
        }
    }
    
    public String getMessages(Map<String, String> filters) throws IOException {
        HttpUrl.Builder urlBuilder = HttpUrl.parse(baseUrl + "/api/client/messages").newBuilder();
        urlBuilder.addQueryParameter("client_code", clientCode);
        
        for (Map.Entry<String, String> entry : filters.entrySet()) {
            urlBuilder.addQueryParameter(entry.getKey(), entry.getValue());
        }
        
        Request request = new Request.Builder()
            .url(urlBuilder.build())
            .addHeader("X-API-Key", apiKey)
            .get()
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            return response.body().string();
        }
    }
}

// Exemplo de uso
public class Main {
    public static void main(String[] args) {
        RCSGatewayClient client = new RCSGatewayClient(
            "https://api.exemplo.com",
            "sua_api_key_aqui",
            "CLI_ABC123"
        );
        
        try {
            // Enviar mensagem de texto
            Map<String, Object> content = Map.of(
                "text", Map.of("message", "Olá! Mensagem de teste do Java.")
            );
            
            String result = client.sendMessage(
                List.of("5511999999999"),
                content,
                "basic",
                "Teste Java"
            );
            
            System.out.println("Resultado: " + result);
            
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

## 🟨 JavaScript/Node.js

### Instalação
```bash
npm install axios
```

### Exemplo
```javascript
const axios = require('axios');

class RCSGatewayClient {
    constructor(baseUrl, apiKey, clientCode) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
        this.clientCode = clientCode;
        this.headers = {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        };
    }
    
    async sendMessage(phoneNumbers, content, messageType = 'basic', options = {}) {
        const payload = {
            client_code: this.clientCode,
            message_type: messageType,
            phone_numbers: phoneNumbers,
            content: content,
            ...options
        };
        
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/client/send-message`,
                payload,
                { headers: this.headers }
            );
            return response.data;
        } catch (error) {
            throw new Error(`Erro ao enviar mensagem: ${error.response?.data?.detail || error.message}`);
        }
    }
    
    async getMessages(filters = {}) {
        const params = { client_code: this.clientCode, ...filters };
        
        try {
            const response = await axios.get(
                `${this.baseUrl}/api/client/messages`,
                { 
                    headers: this.headers,
                    params: params
                }
            );
            return response.data;
        } catch (error) {
            throw new Error(`Erro ao consultar mensagens: ${error.response?.data?.detail || error.message}`);
        }
    }
    
    async getStats() {
        try {
            const response = await axios.get(
                `${this.baseUrl}/api/client/stats`,
                { headers: this.headers }
            );
            return response.data;
        } catch (error) {
            throw new Error(`Erro ao obter estatísticas: ${error.response?.data?.detail || error.message}`);
        }
    }
}

// Exemplo de uso
async function main() {
    const client = new RCSGatewayClient(
        'https://api.exemplo.com',
        'sua_api_key_aqui',
        'CLI_ABC123'
    );
    
    try {
        // Enviar mensagem de texto
        const textResult = await client.sendMessage(
            ['5511999999999'],
            {
                text: {
                    message: 'Olá! Esta é uma mensagem de teste do Node.js.'
                }
            },
            'basic',
            { campaign_name: 'Teste NodeJS' }
        );
        
        console.log('Mensagem enviada:', textResult);
        
        // Enviar Rich Card
        const richCardResult = await client.sendMessage(
            ['5511999999999'],
            {
                richCard: {
                    title: 'Oferta Especial!',
                    description: 'Aproveite nossa promoção especial',
                    fileUrl: 'https://exemplo.com/promocao.jpg',
                    suggestions: [
                        {
                            type: 'openUrl',
                            title: 'Ver Oferta',
                            value: 'https://loja.exemplo.com/promocao'
                        },
                        {
                            type: 'call',
                            title: 'Ligar Agora',
                            value: '1140001234'
                        }
                    ]
                }
            },
            'single'
        );
        
        console.log('Rich Card enviado:', richCardResult);
        
        // Consultar mensagens
        const messages = await client.getMessages({ status: 'delivered', limit: 5 });
        console.log(`Mensagens entregues: ${messages.length}`);
        
        // Obter estatísticas
        const stats = await client.getStats();
        console.log('Estatísticas:', stats);
        
    } catch (error) {
        console.error('Erro:', error.message);
    }
}

main();
```

## 🐘 PHP

### Exemplo
```php
<?php

class RCSGatewayClient {
    private $baseUrl;
    private $apiKey;
    private $clientCode;
    
    public function __construct($baseUrl, $apiKey, $clientCode) {
        $this->baseUrl = $baseUrl;
        $this->apiKey = $apiKey;
        $this->clientCode = $clientCode;
    }
    
    private function makeRequest($method, $endpoint, $data = null) {
        $url = $this->baseUrl . $endpoint;
        
        $headers = [
            'X-API-Key: ' . $this->apiKey,
            'Content-Type: application/json'
        ];
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            if ($data) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
            }
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode >= 400) {
            throw new Exception("Erro HTTP $httpCode: $response");
        }
        
        return json_decode($response, true);
    }
    
    public function sendMessage($phoneNumbers, $content, $messageType = 'basic', $options = []) {
        $payload = array_merge([
            'client_code' => $this->clientCode,
            'message_type' => $messageType,
            'phone_numbers' => $phoneNumbers,
            'content' => $content
        ], $options);
        
        return $this->makeRequest('POST', '/api/client/send-message', $payload);
    }
    
    public function getMessages($filters = []) {
        $params = array_merge(['client_code' => $this->clientCode], $filters);
        $queryString = http_build_query($params);
        
        return $this->makeRequest('GET', '/api/client/messages?' . $queryString);
    }
    
    public function getStats() {
        return $this->makeRequest('GET', '/api/client/stats');
    }
}

// Exemplo de uso
try {
    $client = new RCSGatewayClient(
        'https://api.exemplo.com',
        'sua_api_key_aqui',
        'CLI_ABC123'
    );
    
    // Enviar mensagem de texto
    $textResult = $client->sendMessage(
        ['5511999999999'],
        [
            'text' => [
                'message' => 'Olá! Esta é uma mensagem de teste do PHP.'
            ]
        ],
        'basic',
        ['campaign_name' => 'Teste PHP']
    );
    
    echo "Mensagem enviada: " . json_encode($textResult) . "\n";
    
    // Enviar Rich Card
    $richCardResult = $client->sendMessage(
        ['5511999999999'],
        [
            'richCard' => [
                'title' => 'Oferta Especial!',
                'description' => 'Aproveite nossa promoção',
                'fileUrl' => 'https://exemplo.com/promocao.jpg',
                'suggestions' => [
                    [
                        'type' => 'openUrl',
                        'title' => 'Ver Oferta',
                        'value' => 'https://loja.exemplo.com'
                    ]
                ]
            ]
        ],
        'single'
    );
    
    echo "Rich Card enviado: " . json_encode($richCardResult) . "\n";
    
    // Consultar mensagens
    $messages = $client->getMessages(['status' => 'delivered', 'limit' => 5]);
    echo "Mensagens encontradas: " . count($messages) . "\n";
    
    // Obter estatísticas
    $stats = $client->getStats();
    echo "Estatísticas: " . json_encode($stats) . "\n";
    
} catch (Exception $e) {
    echo "Erro: " . $e->getMessage() . "\n";
}
?>
```

## 🦀 Rust

### Dependências (Cargo.toml)
```toml
[dependencies]
reqwest = { version = "0.11", features = ["json"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1.0", features = ["full"] }
```

### Exemplo
```rust
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize)]
pub struct RCSGatewayClient {
    base_url: String,
    api_key: String,
    client_code: String,
    client: Client,
}

impl RCSGatewayClient {
    pub fn new(base_url: String, api_key: String, client_code: String) -> Self {
        Self {
            base_url,
            api_key,
            client_code,
            client: Client::new(),
        }
    }
    
    pub async fn send_message(
        &self,
        phone_numbers: Vec<String>,
        content: Value,
        message_type: &str,
        options: Option<HashMap<String, Value>>,
    ) -> Result<Value, Box<dyn std::error::Error>> {
        let mut payload = json!({
            "client_code": self.client_code,
            "message_type": message_type,
            "phone_numbers": phone_numbers,
            "content": content
        });
        
        if let Some(opts) = options {
            for (key, value) in opts {
                payload[key] = value;
            }
        }
        
        let response = self
            .client
            .post(&format!("{}/api/client/send-message", self.base_url))
            .header("X-API-Key", &self.api_key)
            .header("Content-Type", "application/json")
            .json(&payload)
            .send()
            .await?;
        
        let result: Value = response.json().await?;
        Ok(result)
    }
    
    pub async fn get_messages(
        &self,
        filters: Option<HashMap<String, String>>,
    ) -> Result<Value, Box<dyn std::error::Error>> {
        let mut params = vec![("client_code", self.client_code.clone())];
        
        if let Some(f) = filters {
            for (key, value) in f {
                params.push((key.as_str(), value));
            }
        }
        
        let response = self
            .client
            .get(&format!("{}/api/client/messages", self.base_url))
            .header("X-API-Key", &self.api_key)
            .query(&params)
            .send()
            .await?;
        
        let result: Value = response.json().await?;
        Ok(result)
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = RCSGatewayClient::new(
        "https://api.exemplo.com".to_string(),
        "sua_api_key_aqui".to_string(),
        "CLI_ABC123".to_string(),
    );
    
    // Enviar mensagem de texto
    let content = json!({
        "text": {
            "message": "Olá! Esta é uma mensagem de teste do Rust."
        }
    });
    
    let mut options = HashMap::new();
    options.insert("campaign_name".to_string(), json!("Teste Rust"));
    
    let result = client
        .send_message(
            vec!["5511999999999".to_string()],
            content,
            "basic",
            Some(options),
        )
        .await?;
    
    println!("Mensagem enviada: {}", result);
    
    // Consultar mensagens
    let mut filters = HashMap::new();
    filters.insert("status".to_string(), "delivered".to_string());
    filters.insert("limit".to_string(), "5".to_string());
    
    let messages = client.get_messages(Some(filters)).await?;
    println!("Mensagens: {}", messages);
    
    Ok(())
}
```

## 🔧 Configuração de Webhook (Opcional)

Se você quiser receber callbacks em tempo real sobre o status das mensagens:

### Endpoint de Callback
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/rcs-callback', methods=['POST'])
def rcs_callback():
    """Recebe callbacks do RCS Gateway"""
    data = request.get_json()
    
    # Processar callback
    message_id = data.get('message_id')
    status = data.get('status')
    phone_number = data.get('phone_number')
    
    print(f"Mensagem {message_id} para {phone_number}: {status}")
    
    # Salvar no seu banco de dados
    # update_message_status(message_id, status)
    
    return jsonify({"status": "received"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Configurar Callback na Mensagem
```python
result = client.send_message(
    phone_numbers=['5511999999999'],
    content={'text': {'message': 'Teste com callback'}},
    callback_url='https://seu-dominio.com/rcs-callback'
)
```

---

**💡 Dicas:**
1. Sempre trate erros adequadamente
2. Implemente retry para falhas temporárias
3. Use logs para debug
4. Mantenha sua API Key segura
5. Teste em ambiente de desenvolvimento primeiro
