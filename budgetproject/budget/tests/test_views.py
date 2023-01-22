from django.test import TestCase, Client
from django.urls import reverse
from budget.models import Project, Category, Expense
import json

# assertEquals(1, 2) ->  1 == 2

class TestViews(TestCase):

	# Ustawianie danych pomocniczych
	def setUp(self):
		self.client = Client()
		self.list_url = reverse('list')
		self.detail_url = reverse('detail', args=['project1'])
		self.project1 = Project.objects.create(
			name='project1',
			budget=10000,
		)


	def test_project_list_GET(self):

		response = self.client.get(self.list_url)
		# Sprawdza czy widok 'list' zwraca status 200
		self.assertEquals(response.status_code, 200)
		# Sprawdza czy widok 'list' używa prawidłowej templatki
		self.assertTemplateUsed(response, 'budget/project-list.html')

	def test_project_detail_GET(self):
		response = self.client.get(self.detail_url)
		# Sprawdza czy widok 'detail' zwraca status 200
		self.assertEquals(response.status_code, 200)
		# Sprawdza czy widok 'detail' używa prawidłowej templatki
		self.assertTemplateUsed(response, 'budget/project-detail.html')

	# Testowanie działania request.POST z danymi
	def test_project_detail_POST_adds_new_expense(self):
		# Stworzenie Category
		Category.objects.create(
			project = self.project1,
			name='development'
		)

		# wykonanie request.POST do utworzenia expense
		response = self.client.post(self.detail_url, {
				'title': 'expense1',
				'amount': 1000,
				'category': 'development'
			}
		)

		# sprawdzenie status code
		self.assertEquals(response.status_code, 302)
		# sprawdzenie czy Expense zostało utworzone
		self.assertEquals(self.project1.expenses.first().title, 'expense1')

	# Testowanie działania request.POST bez danych w widoku 'detail'
	def test_project_detail_POST_no_data(self):

		# wykonanie request.POST bez danych
		response = self.client.post(self.detail_url)

		# sprawdzenie status code
		self.assertEquals(response.status_code, 302)
		# sprawdzenie czy na pewno expense nie zostało utworzone
		self.assertEquals(self.project1.expenses.count(),0)

	# Testowanie działania request.Delete z danymi w widoku 'detail'
	def test_project_detail_DELETE_deletes_expense(self):

		# stworzenie Category
		category1 = Category.objects.create(
			project=self.project1,
			name='development'
		)

		# stworzenie Expense
		expense = Expense.objects.create(
			project=self.project1,
			title='expense1',
			amount=10000,
			category=category1,
		)

		# Wykonanie request.delete z danymi
		response = self.client.delete(
			self.detail_url, 
			json.dumps({'id': expense.id})
		)

		# sprawdzenie status code
		self.assertEquals(response.status_code, 204)
		# sprawdzenie czy expense zostało usunięte poprzez sprawdzenie ilości
		self.assertEquals(self.project1.expenses.count(),0)


	# Testowanie działania request.Delete bez danych w widoku 'detail'
	def test_project_detail_DELETE_no_id(self):

		# Stworzenie kategorii
		category1 = Category.objects.create(
			project=self.project1,
			name='development'
		)

		# Stworzenie Expense
		expense = Expense.objects.create(
			project=self.project1,
			title='expense1',
			amount=10000,
			category=category1,
		)

		# wykonanie request.delete bez danych
		response = self.client.delete(
			self.detail_url
		)

		# sprawdzenie status code
		self.assertEquals(response.status_code, 404)
		# sprawdzenie czy expense nie zostało usunięte
		self.assertEquals(self.project1.expenses.count(),1)


	# testowanie tworzenia projektu w widoku 'add'
	def test_project_create_POST(self):
		url = reverse('add')

		# request.Post z danymi projektu, categoriesString zawiera nazwy dwóch kategorii
		response = self.client.post(url, {
			'name': 'project2',
			'budget': 10000,
			'categoriesString': 'design,development'
		})

		# sprawdzenie czy projekt został utworzony
		project2 = Project.objects.get(id=2)
		self.assertEquals(project2.name, 'project2')

		# sprawdzenie czy została utworzona pierwsza kategoria
		first_category = Category.objects.get(id=1)
		self.assertEquals(first_category.project, project2)
		self.assertEquals(first_category.name, 'design')
		# sprawdzenie czy została utworzona druga kategoria
		second_category = Category.objects.get(id=2)
		self.assertEquals(second_category.project, project2)
		self.assertEquals(second_category.name, 'development')