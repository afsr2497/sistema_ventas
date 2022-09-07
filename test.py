from apis_net_pe import ApisNetPe
# Usar token personal
APIS_TOKEN = "apis-token-1.aTSI1U7KEuT-6bbbCguH-4Y8TI6KS73N"

api_consultas = ApisNetPe(APIS_TOKEN)
# Api Consulta ruc sunat
print(api_consultas.get_company("20601502373"))
# Api consulta tipo de cambio del dia sunata