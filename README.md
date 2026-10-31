# API-тесты Stellar Burgers

Проект проверяет API Stellar Burgers: регистрацию и вход пользователей, изменение профиля, создание заказа и получение заказов.

## Установка

Создайте виртуальное окружение и установите зависимости:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Запуск тестов и Allure

Запустите тесты и сохраните результаты:

```powershell
pytest --clean-alluredir --alluredir=allure-results
```

Чтобы открыть отчет Allure, выполните:

```powershell
allure serve allure-results
```
