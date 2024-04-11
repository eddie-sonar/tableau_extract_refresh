import tableauserverclient as TSC
import os

token_name = os.environ.get("TOKEN_NAME")
token_value = os.environ.get("TOKEN_VALUE")
site_name = os.environ.get("SITENAME")
server_url = "https://" + os.environ.get("SERVER_URL")

tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_name)
server = TSC.Server(server_url)
server.version = '3.1'
server.add_http_options({'verify': False})
server.auth.sign_in(tableau_auth)

job_ids = ['d2699697-8d15-4d81-a66a-b84a74816440', '2292314a-09bd-49fd-9757-4127418b51ac', '65210762-0f05-4000-bb9f-7d9bc6c49533', '0af37ef6-6dec-45bc-936d-034f0115e120', '6afcbf46-9d35-43ae-8fbe-9323d45a85f9', 'cdf9cdd6-7fc0-4b32-847e-dec24524f449', 'b1154b0b-8715-465d-8cc7-3e18738f940d', '06623465-e777-4802-ad48-5d6f727723a2', '089ea5cd-770d-4615-bac8-2bf4666d72c2', '6830f514-07bc-43f0-a08f-916462c26f4c', 'a6562ca6-50cf-4100-afc1-178ce5c6360b', '84ee4d7b-ceb8-4328-a8b7-e641708ae5f9', '38f298d6-ac0e-4799-8667-0ee38f18b6e5', 'd324ab84-9b36-451d-9d9f-0c23ee64ed57', 'ba3896cf-948e-4e97-9314-4a3f0775037f', 'c5f5ecb8-8306-42a5-981e-5c1724af6680', 'da104aa9-2c5f-47b5-8a36-dbbef88c1cc1', '4d502237-2534-46c1-b179-069af9d6cbec', 'a27aa0f8-e19b-4fd7-b88d-5d05e90b8b0c']

for id in job_ids:
    server.jobs.cancel(id)
