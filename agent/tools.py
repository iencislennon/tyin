from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()

@tool('calcuale_annuity_payment', description="""Рассчитывает ежемесячный аннуитетный платёж по кредиту.
Используй когда пользователь спрашивает: ежемесячный платёж, сколько платить в месяц, аннуитетный график.
Параметры: credit_sum (сумма кредита), annual_rate (годовая ставка в %), months (срок в месяцах).
""")

def calc_annuity_payment(credit_sum, annual_rate:float, months:int):

    r = (annual_rate/ 12) /100
    A = credit_sum * (r * (1+r)**months) / ((1+r)**months - 1) # A это и есть аннуитетный ежемесячный платеж
    return A 

@tool('calculate_full_payment', description= """
    Рассчитывает общую сумму всех выплат по кредиту за весь срок.
Используй когда пользователь спрашивает: сколько всего заплачу, итоговая сумма выплат, общая стоимость кредита.
Параметры: principal (сумма кредита), annual_rate (годовая ставка в %), months (срок в месяцах).
    """)

def calc_full_payment(principal, annual_rate:float, months:int):

    r = (annual_rate/ 12) /100
    A = principal * (r * (1+r)**months) / ((1+r)**months - 1)
    total_payment = A * months
    return total_payment

@tool('calculate_overpayment', description="""
        Рассчитывает переплату — разницу между общими выплатами и телом кредита.
Используй когда пользователь спрашивает: сколько переплачу, стоимость кредита, переплата по процентам.
Параметры: principal (сумма кредита), annual_rate (годовая ставка в %), months (срок в месяцах).
    """)
def calc_overpayment(principal, annual_rate:float, months:int):

    r = (annual_rate/ 12) /100
    A = principal * (r * (1+r)**months) / ((1+r)**months - 1)
    total_payment = A * months
    overpayment = total_payment - principal
    return overpayment