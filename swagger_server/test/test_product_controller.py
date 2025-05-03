# coding: utf-8

from __future__ import absolute_import

from flask import json

from swagger_server.models.product import Product  # noqa: E501
from swagger_server.test import BaseTestCase


class TestProductController(BaseTestCase):
    """ProductController integration test stubs"""

    def test_add_product(self):
        """Test case for add_product

        Создать товар
        """
        body = Product()
        response = self.client.open(
            '/v1/products',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_product(self):
        """Test case for delete_product

        Удалить товар
        """
        response = self.client.open(
            '/v1/products/{id}'.format(id='id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_all_categories(self):
        """Test case for get_all_categories

        Получить все категории товаров
        """
        response = self.client.open(
            '/v1/products/categories',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_product_by_id(self):
        """Test case for get_product_by_id

        Найти товар по ID
        """
        response = self.client.open(
            '/v1/products/{id}'.format(id='id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_search_products_by_category(self):
        """Test case for search_products_by_category

        Поиск товаров по категории
        """
        query_string = [('category', 'category_example')]
        response = self.client.open(
            '/v1/products/search',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_product(self):
        """Test case for update_product

        Обновить существующий товар
        """
        body = Product()
        response = self.client.open(
            '/v1/products/{id}'.format(id='id_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
