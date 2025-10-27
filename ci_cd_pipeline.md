# CI/CD pipeline для телеграм-бота для фрилансеров

## Общая информация

Данный документ описывает процесс непрерывной интеграции и доставки (CI/CD) для телеграм-бота для фрилансеров. CI/CD pipeline обеспечивает автоматизацию процессов тестирования, сборки, тестирования и развертывания приложения при каждом изменении кода.

## Архитектура CI/CD pipeline

```
[Код в репозитории] -> [Триггер] -> [Сборка] -> [Тестирование] -> [Сборка Docker образа] -> [Развертывание]
```

### Этапы pipeline

1. **Инициализация** - запуск процесса при пуше в репозиторий
2. **Сборка** - установка зависимостей и подготовка окружения
3. **Тестирование** - запуск юнит-тестов и интеграционных тестов
4. **Сборка Docker образа** - создание Docker образа приложения
5. **Развертывание** - развертывание обновленного образа на сервере

## GitHub Actions (рекомендуемый вариант)

### .github/workflows/ci_cd.yml

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run unit tests
      run: |
        pytest tests/ -v --cov=src --cov-report=xml

    - name: Upload coverage reports to Codecov
      uses: codecov/codecov-action@v3
      env:
        CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./bot/Dockerfile
        push: true
        tags: |
          ${{ secrets.DOCKERHUB_USERNAME }}/frilans-bot:${{ github.sha }}
          ${{ secrets.DOCKERHUB_USERNAME }}/frilans-bot:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: [self-hosted, linux, x64]
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Pull latest Docker image
      run: |
        docker pull ${{ secrets.DOCKERHUB_USERNAME }}/frilans-bot:latest

    - name: Stop running containers
      run: |
        docker-compose down

    - name: Start new containers
      run: |
        docker-compose up -d
        docker system prune -f

    - name: Run post-deployment tests
      run: |
        # Добавить сюда тесты, проверяющие работоспособность после деплоя
        docker-compose ps
```

### Требуемые секреты в GitHub

Для работы pipeline необходимы следующие секреты, которые должны быть добавлены в настройках репозитория:

- `DOCKERHUB_USERNAME` - имя пользователя DockerHub
- `DOCKERHUB_TOKEN` - токен доступа к DockerHub
- `CODECOV_TOKEN` - токен для Codecov (опционально)

## GitLab CI/CD (альтернативный вариант)

### .gitlab-ci.yml

```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

before_script:
  - docker info

test:
  stage: test
  image: python:3.9
  services:
    - postgres:13
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_password
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest tests/ -v --cov=src
  coverage: '/TOTAL.*\s(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build_image:
  stage: build
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
 before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - main
    - develop

deploy_staging:
  stage: deploy
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  before_script:
    - 'command -v ssh-agent >/dev/null || ( apt-get update -y && apt-get install openssh-client -y )'
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - echo "$SSH_KNOWN_HOSTS" >> ~/.ssh/known_hosts
    - chmod 644 ~/.ssh/known_hosts
  script:
    - ssh $DEPLOY_USER@$STAGING_HOST "cd /opt/frilans_bot && git pull origin develop && docker-compose down && docker-compose up -d"
  environment:
    name: staging
  only:
    - develop

deploy_production:
  stage: deploy
 image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  before_script:
    - 'command -v ssh-agent >/dev/null || ( apt-get update -y && apt-get install openssh-client -y )'
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - echo "$SSH_KNOWN_HOSTS" >> ~/.ssh/known_hosts
    - chmod 644 ~/.ssh/known_hosts
  script:
    - ssh $DEPLOY_USER@$PRODUCTION_HOST "cd /opt/frilans_bot && git pull origin main && docker-compose down && docker-compose up -d"
  environment:
    name: production
  when: manual
  only:
    - main
```

## Тестирование в CI/CD

### Юнит-тесты

Для юнит-тестирования используется фреймворк pytest. Пример структуры тестов:

```
tests/
├── test_bot_core.py
├── test_data_collector.py
├── test_filter_engine.py
├── test_personalization_engine.py
├── test_notification_engine.py
├── test_data_storage.py
└── conftest.py
```

### Интеграционные тесты

Интеграционные тесты проверяют взаимодействие между компонентами системы. Они могут включать:

- Тестирование взаимодействия с внешними API
- Тестирование работы с базой данных
- Тестирование отправки уведомлений

### Тесты производительности

Для оценки производительности системы в CI/CD могут включаться:

- Тесты нагрузки с использованием Apache Bench или JMeter
- Тесты утечек памяти
- Тесты времени отклика

## Безопасность в CI/CD

### Сканеры безопасности

В pipeline рекомендуется включить сканеры безопасности:

```yaml
security-scan:
  stage: test
 image: aquasec/trivy
  script:
    - trivy image --exit-code 0 $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - trivy fs --exit-code 0 .
  allow_failure: true
```

### Проверка зависимостей

Проверка зависимостей на наличие уязвимостей:

```yaml
dependency-check:
  stage: test
  image: python:3.9
  script:
    - pip install safety
    - safety check
```

## Мониторинг и оповещения

### Slack-уведомления

Для получения уведомлений о статусе сборки можно использовать интеграцию со Slack:

```yaml
notifications:
  stage: deploy
  image: curlimages/curl
  script:
    - |
      if [ "$CI_COMMIT_REF_NAME" = "main" ]; then
        curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"Deployment to production successful! \nCommit: '"$CI_COMMIT_MESSAGE"' \nAuthor: '"$GITLAB_USER_NAME"'"}' \
        $SLACK_WEBHOOK_URL
      fi
  when: on_success
```

## План внедрения

### Этап 1: Подготовка (дни 1-3)

1. Создание файлов конфигурации CI/CD (`.github/workflows/ci_cd.yml` или `.gitlab-ci.yml`)
2. Настройка секретов в репозитории
3. Подготовка Dockerfile для контейнеризации

### Этап 2: Тестирование (дни 4-7)

1. Настройка юнит-тестов
2. Настройка интеграционных тестов
3. Проверка работоспособности pipeline

### Этап 3: Развертывание (дни 8-10)

1. Настройка развертывания на staging-сервере
2. Настройка развертывания на production-сервере
3. Тестирование автоматического развертывания

### Этап 4: Мониторинг и оптимизация (дни 11-14)

1. Настройка уведомлений
2. Оптимизация времени выполнения pipeline
3. Настройка безопасности

## Запуск локально (для отладки)

Для отладки CI/CD pipeline локально можно использовать следующие инструменты:

### Для GitHub Actions

Использование `act` для запуска GitHub Actions локально:

```bash
# Установка act
brew install act # для macOS
# или
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Запуск workflow локально
act
```

### Для GitLab CI

Использование `gitlab-ci-local` для запуска GitLab CI локально:

```bash
# Установка gitlab-ci-local
npm install -g gitlab-ci-local

# Запуск pipeline локально
gitlab-ci-local
```

## Заключение

CI/CD pipeline обеспечивает автоматизацию процессов разработки, тестирования и развертывания телеграм-бота для фрилансеров. Правильно настроенный pipeline позволяет:

- Ускорить процесс разработки
- Снизить количество ошибок при развертывании
- Обеспечить стабильность и надежность системы
- Упростить процесс внесения изменений