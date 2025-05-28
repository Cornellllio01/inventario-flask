from supabase import create_client, Client

url = "https://lxrzmysrrcqcabhxfeti.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx4cnpteXNycmNxY2FiaHhmZXRpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgzNDk3MzAsImV4cCI6MjA2MzkyNTczMH0.UE-nVgvSZjX4I4E5AB1sAAdCOaK46C4I2aYkDhn52dA"

supabase: Client = create_client(url, key)

res = supabase.table("nome_da_tabela").select("*").limit(1).execute()
print(res.data)
