import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = 'https://apc.kz/'
visited_urls = set()
data = []


def get_soup(url):
	response = requests.get(url)
	return BeautifulSoup(response.text, 'html.parser')


def get_categories(soup):
	categories = []
	for category in soup.select('.col-lg-2.col-md-3.col-sm-4.col-xs-6'):
		category_name = category.select_one('h4 a').text.strip()
		category_link = category.select_one('h4 a')['href']
		if category_link not in visited_urls:
			visited_urls.add(category_link)
			categories.append((category_name, category_link))
	return categories


def get_subcategories(category_url):
	soup = get_soup(category_url)
	subcategories = []
	for subcategory in soup.select('.refine_categories a'):
		subcategory_name = subcategory.select_one('span').text.strip()
		subcategory_link = subcategory['href']
		if subcategory_link not in visited_urls:
			visited_urls.add(subcategory_link)
			subcategories.append((subcategory_name, subcategory_link))
	return subcategories


def get_products(subcategory_url):
	soup = get_soup(subcategory_url)
	products = []
	for product in soup.select('.product-layout'):
		product_name = product.select_one('.caption h4 a span').text.strip()
		product_link = product.select_one('.caption h4 a')['href']
		if product_link not in visited_urls:
			visited_urls.add(product_link)
			products.append((product_name, product_link))
	return products


def get_product_details(product_url):
	soup = get_soup(product_url)
	details = {}
	for row in soup.select('tr[itemprop="additionalProperty"]'):
		name = row.select_one('td[itemprop="name"]').text.strip()
		value = row.select_one('td[itemprop="value"]').text.strip()
		details[name] = value
	return details


def main():
	soup = get_soup(URL)
	categories = get_categories(soup)
	print(f'Найдено категорий: {len(categories)}')

	for category_name, category_link in categories:
		print(f'Парсинг категории: {category_name}')
		subcategories = get_subcategories(category_link)
		if not subcategories:
			print(f'  В категории "{category_name}" нет подкатегорий, ищем товары...')
			products = get_products(category_link)
			for product_name, product_link in products:
				print(f'    Найден товар: {product_name}')
				details = get_product_details(product_link)
				details['Категория'] = category_name
				details['Подкатегория'] = ''
				details['Товар'] = product_name
				details['Ссылка'] = product_link
				data.append(details)
		else:
			for subcategory_name, subcategory_link in subcategories:
				print(f'  Парсинг подкатегории: {subcategory_name}')
				products = get_products(subcategory_link)
				for product_name, product_link in products:
					print(f'    Найден товар: {product_name}')
					details = get_product_details(product_link)
					details['Категория'] = category_name
					details['Подкатегория'] = subcategory_name
					details['Товар'] = product_name
					details['Ссылка'] = product_link
					data.append(details)

	df = pd.DataFrame(data)
	columns_order = ['Категория', 'Подкатегория', 'Товар', 'Ссылка'] + [col for col in df.columns if col not in ['Категория', 'Подкатегория', 'Товар', 'Ссылка']]
	df = df[columns_order]

	df.to_excel('APC_data.xlsx', index=False)
	print('Данные записаны в файл APC_data.xlsx')


if __name__ == '__main__':
	main()
