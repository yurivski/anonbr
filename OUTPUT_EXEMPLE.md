## Exemplos de outputs em cada nível de censura

A biblioteca oferece três níveis de privacidade. Cada nível controla quanta informação fica visível após o mascaramento.

> **High:** Oculta toda a informação. Útil quando nenhum dado pode ser revelado.  
**Low:** Revela mais informação. Útil para conferência em ambientes controlados.  
**Default:** Revela uma parte pequena para conferência, sem expor o dado completo.

---

|**Extensão**|**Nivel**|**CPF**|**Telefone**|**E-Mail**| **CNPJ**|
|------------|---------|-------|------------|----------|-----------|
||**HIGH**|XXX.XXX.XXX-XX | +XX (XX) XXXXX-XXXX | xxxxxxxxx@xxxxx.xxx |XX.XXX.XXX/XXXX-XX|
|**CSV**|**LOW**| XXX.XX6.646-08 | +55 (21) XXXX5-4321 | xxxxosilva@empresa.com.br |XX.XXX.XXX/1098-65|
||**DEFAULT**| XXX.096.XXX-XX | +55 (21) XXXXX-4321 | bxxxxxxxxx@empresa.com.br |XX.765.432/XXXX-XX|
|-|-|-|-|-|
||**HIGH**|███.███.███-██ | ███ (██) █████-████ | ██████████@██████.███ |██.███.███/████-██|
|**PDF**|**LOW**|███.██6.646-08 | +55 (21) ████5-5678 | ████osilva@empresa.com.br |██.███.███/1098-65|
||**DEFAULT**|███.096.███-██ | +55 (21) █████-5678 | b███osilva@gmail.com |██.765.432/████-██|

---

![Exemplo de output](/images/exemplo_output_v1.2.png)

