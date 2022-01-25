import datetime
import argparse

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from AccountInfo import AccountInfo

transport = AIOHTTPTransport(url="https://api.eonnext-kraken.energy/v1/graphql/")
client = Client(transport=transport, fetch_schema_from_transport=True)

parser = argparse.ArgumentParser(description="Submit electricity and gas meter readings to Sainsbury's Energy")
parser.add_argument('--email', action="store", type=str, required=True, help="Your Sainsbury's Energy account email")
parser.add_argument('--password', action="store", type=str, required=True,
                    help="Your Sainsbury's Energy account password")
parser.add_argument('--gas', action="store", type=int, help="An integer value to submit as the gas meter reading")
parser.add_argument('--elec', action="store", type=int,
                    help="An integer value to submit as the electricity meter reading")
args = parser.parse_args()


def get_refresh_token(password: str, email: str):
    token_mutation = gql(
        f"""
        mutation getToken1 {{
          obtainKrakenToken(input: {{
            email: "{email}",
            password: "{password}"
          }}){{
            token
          }}
        }}
        """
    )

    result = client.execute(token_mutation)

    token = result["obtainKrakenToken"]["token"]

    print(f"Token obtained: {token[:10]}...")

    return token


def get_account_number():
    query = gql(
        f"""
        query viewer{{
          viewer {{
            accounts {{
                number
            }}
          }}
        }}
        """
    )

    result = client.execute(query)

    result_number = result["viewer"]["accounts"][0]["number"]

    print(f"Account number obtained: {result_number}")

    return result_number


def get_meter_info(ac_no: str):
    query = gql(
        f"""
        query getAccount{{
          account(accountNumber: "{ac_no}"){{
            id, status, properties {{
              id, electricityMeterPoints {{
                id, mpan, meters {{
                  serialNumber, registers {{
                    identifier
                  }}
                }}
              }}, gasMeterPoints {{
                id, mprn, meters {{
                  serialNumber, registers {{
                    id
                  }}
                }}
              }}
            }}
          }}
        }}
        """
    )

    result = client.execute(query)

    result_obj = AccountInfo(result)

    print(f"Meter info obtained: {result_obj}")

    return result_obj


def submit_gas_reading(account_info: AccountInfo, reading: int, reading_date: datetime.date = datetime.date.today()):
    print(
        f"Submitting gas reading of {reading} for {reading_date} for MPRN {account_info.mprn} with serial {account_info.gas_meter_serial}")

    gas_reading_mutation = gql(
        f"""
        mutation gasReading {{
          createGasMeterReading(
            mprn: "{account_info.mprn}",
            serialNumber: "{account_info.gas_meter_serial}",
            readAt: "{reading_date}",
            reading: {reading}
          ) {{
            readingErrors{{
              field
            }}
          }}
        }}
        """
    )

    result = client.execute(gas_reading_mutation)

    if result['createGasMeterReading'] is None:
        return True
    else:
        return False


def submit_electricity_reading(account_info: AccountInfo, reading: int,
                               reading_date: datetime.date = datetime.date.today()):
    print(
        f"Submitting electricity reading of {reading} with register {account_info.electricity_register} for {reading_date} for MPAN {account_info.mpan} with serial {account_info.electricity_meter_serial}")

    electricity_reading_mutation = gql(
        f"""
        mutation electricityReading {{
          createElectricityMeterReading(
            mpan: "{account_info.mpan}",
            serialNumber: "{account_info.electricity_meter_serial}",
            readAt: "{reading_date}",
            readings: {{
                reading: {reading},
                register: "{account_info.electricity_register}"
            }}
          ) {{
            readingErrors{{
              field
            }}
          }}
        }}
        """
    )

    result = client.execute(electricity_reading_mutation)

    if result['createElectricityMeterReading'] is None:
        return True
    else:
        return False


if __name__ == '__main__':

    try:
        jwt = f"JWT {get_refresh_token(email=args.email, password=args.password)}"
    except TransportQueryError:
        raise ConnectionRefusedError("Unable to get token, please check creds")

    transport.headers = {"Authorization": jwt}

    account_number = get_account_number()

    fetched_account_info = get_meter_info(account_number)

    gas_success = False
    electricity_success = False

    if args.gas is not None:
        gas_success = submit_gas_reading(fetched_account_info, 943)

    if args.elec is not None:
        electricity_success = submit_electricity_reading(fetched_account_info, 2799)

    print(
        f"""Electricity ⚡️: {"Success 😎" if electricity_success else "Failed ☹️"}
        Gas 🔥: {"Success 😎" if gas_success else "Failed ☹️"}
        """
    )
