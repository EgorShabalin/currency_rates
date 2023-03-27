import aiohttp
import asyncio
import argparse
from datetime import timedelta
from dateutil import parser as date_parser


URL = "https://api.exchangerate.host/"

parser = argparse.ArgumentParser(
    prog="=====CURRENCY RATES=====",
    description="""Shows currency rates to base
                    currency and in history view.""",
)

subparser = parser.add_subparsers(dest="cmd")
get_list_of_currencies = subparser.add_parser("symbols", help="Get list of currencies")
get_list_of_currencies.add_argument(
    "-from",
    "--currency_from",
    type=str,
    dest="currency_from",
    help="Enter base currency",
)
get_list_of_currencies.add_argument(
    "-to",
    "--currency_to",
    type=str,
    dest="currency_to",
    help="Enter currencies to convert to",
)
get_list_of_currencies.add_argument(
    "-a", "--amount", type=int, dest="amount", default="1", help="Amount of currency"
)

convert_currency = subparser.add_parser(
    "convert", help="Convert currency for today or choosen date"
)
convert_currency.add_argument(
    "-from",
    "--currency_from",
    type=str,
    dest="currency_from",
    help="Enter base currency",
)
convert_currency.add_argument(
    "-to",
    "--currency_to",
    type=str,
    dest="currency_to",
    help="Enter currencies to convert to",
)
convert_currency.add_argument(
    "-d", "--date", type=str, dest="date_from", help="Enter date"
)
convert_currency.add_argument("amount_convert", type=int, help="Amount of currency")


get_history_rates = subparser.add_parser(
    "history", help="Get currency rates on choosen dates"
)
get_history_rates.add_argument(
    "-from",
    "--currency_from",
    type=str,
    dest="currency_from",
    help="Enter base currency",
)
get_history_rates.add_argument(
    "-to",
    "--currency_to",
    type=str,
    dest="currency_to",
    help="Enter currencies to convert to",
)
get_history_rates.add_argument(
    "-date_from", "--df", type=str, dest="date_from", help="Enter date from"
)
get_history_rates.add_argument(
    "-date_to", "--dt", type=str, dest="date_to", help="Enter date to"
)
get_history_rates.add_argument("amount_history", type=int, help="Amount of currency")


args = parser.parse_args()

sema = asyncio.Semaphore(100)


async def get_currencies(session, currency_from, currency_to, amount) -> str:
    async with session.get(
        f"{URL}latest?base={currency_from}&symbols={currency_to}&amount={amount}"
    ) as response:
        currencies = await response.json()
        print(
            f"""{currencies['success']}\n\r
        {currencies['base']}\n\r
        {currencies['date']}\n\r
        {currencies['rates']}"""
        )


async def convert_currency(
    session, currency_from, currency_to, date_from, amount
) -> str:
    if date_from:
        date_from = date_parser.parse(date_from)
    else:
        pass
    async with session.get(
        f"{URL}convert?from={currency_from}&to={currency_to}&amount={amount}&date={date_from}"
    ) as response:
        result = await response.json()
        print(
            f"""{result['success']}\n\r
        {result['query']}\n\r
        {result['info']}\n\r
        {result['date']}\n\r
        {result['result']}"""
        )


async def get_rate(session, sema, currency_from, currency_to, this_date, amount) -> str:
    async with session.get(
        f"{URL}{this_date}?base={currency_from}&symbols={currency_to}&amount={amount}"
    ) as response:
        rate = await response.json()
        print(
            f"""{rate['success']}\n\r
            {rate['base']}\n\r
            {rate['date']}\n\r
            {rate['rates']}"""
        )


async def history(session, sema, currency_from, currency_to, start, end, amount):
    start = date_parser.parse(start)
    end = date_parser.parse(end)
    numdays = end - start
    tasks = []
    for d in range(int(numdays.days) + 1):
        day = start + timedelta(d)
        task = asyncio.ensure_future(
            get_rate(session, sema, currency_from, currency_to, day, amount)
        )
        tasks.append(task)
    async with sema:
        await asyncio.wait(tasks)


async def main():
    async with aiohttp.ClientSession() as session:
        if args.cmd == "symbols":
            await get_currencies(
                session, args.currency_from, args.currency_to, args.amount
            )
        if args.cmd == "convert":
            await convert_currency(
                session,
                args.currency_from,
                args.currency_to,
                args.date_from,
                args.amount_convert,
            )
        if args.cmd == "history":
            await history(
                session,
                sema,
                args.currency_from,
                args.currency_to,
                args.date_from,
                args.date_to,
                args.amount_history,
            )


asyncio.run(main())
