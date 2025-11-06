# 🛒 Shopping Cart System with Flexible Pricing Rules

A sophisticated Django REST Framework-based shopping cart system featuring a highly flexible pricing rules engine that allows dynamic pricing strategies without code changes.

## ✨ Features

- **🧠 Flexible Pricing Engine**: Define complex pricing rules via database - no code deployment needed
- **🚀 Django REST Framework**: Robust and scalable API architecture
- **🐘 PostgreSQL**: Production-ready database
- **🐳 Docker Containerized**: Easy deployment with Docker Compose
- **⚡ Redis**: High-performance caching
- **🎯 Rule Priority System**: Intelligent rule application order
- **📊 Comprehensive API**: Full-featured REST endpoints

## 🏗️ Architecture Highlights

### Dynamic Pricing Rules
- **Percentage Discounts**: Automatic percentage-based discounts
- **Fixed Amount Discounts**: Straightforward price reductions
- **Buy X Get Y Free**: Promotional quantity-based rules
- **Bundle Discounts**: Cross-product package deals
- **Custom Conditions**: Minimum totals, quantities, product-specific rules

### Installation
## Clone repository
```
git clone https://github.com/irAbs174/shopping_cart.git
cd shopping_cart
```
## Start services
```
docker-compose up --build
```
## Run migrations
```
docker-compose exec web python manage.py migrate
```
## Create sample data
```
docker-compose exec web python manage.py create_sample_data
```