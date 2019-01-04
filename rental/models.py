from django.db import models
from django.core.exceptions import ValidationError
import json

class Car(models.Model):
	class Meta:
		verbose_name = "车辆"
		verbose_name_plural = "车辆"
		ordering = ['car_name']
	car_name = models.CharField(max_length=100, verbose_name="车辆名称")
	make = models.CharField(max_length=50, verbose_name="制造商")
	engine_identification=models.CharField(max_length=20, verbose_name="引擎编号")
	color=models.CharField(max_length=50, verbose_name="颜色")
	plateName=models.CharField(max_length=50, verbose_name="车牌号")
	def __str__(self):
		return self.car_name

class Reservation(models.Model):
	class Meta:
		verbose_name = "预约"
		verbose_name_plural = "预约"
	PAYMENT_TYPE_CHOICES = (
		('CASH', '现金'),
		('CARD', '信用卡'),
	)
	customer = models.ForeignKey('Customer', verbose_name="顾客", on_delete=models.CASCASE,)
	car = models.ForeignKey('Car', verbose_name="车辆", on_delete=models.CASCASE,)
	startDate = models.DateField(verbose_name="取车日期")
	endDate = models.DateField(verbose_name="还车日期（必须在取车日期之后）")
	total_amount = models.IntegerField(verbose_name="单价") # To avoid the trouble of syncing DB, I keep using the total_amount for daily rate
	security_deposit_return = models.BooleanField(verbose_name="押金退还")
	payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, verbose_name="付款方式")
	def __str__(self):
		return str(self.car)+'|'+str(self.customer)+'|'+str(self.startDate)+'~'+str(self.endDate)
	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
	def clean(self):
		if self.total_amount <=0:
			raise ValidationError('单价不能小于或等于0')
		if self.startDate >= self.endDate:
			raise ValidationError('还车日期应该在取车日期之后！')

class Customer(models.Model):
	class Meta:
		verbose_name = "顾客"
		verbose_name_plural = "顾客"
	MALE = 'M'
	FEMALE = 'F'
	GENDER_CHOICES = (
		(MALE, '男'),
		(FEMALE, '女'),
	)
	name = models.CharField(max_length=100, verbose_name="姓名")
	birth_day = models.DateField(verbose_name="生日")
	gender = models.CharField(max_length=20, choices=GENDER_CHOICES, verbose_name="性别")
	license_number = models.CharField(max_length=50, verbose_name="驾驶证号")
	ID_number = models.CharField(max_length=60, verbose_name="身份证号")
	hometown = models.CharField(max_length=50, verbose_name="家乡")
	phone_number = models.CharField(max_length=20, verbose_name="电话号码")
	def __str__(self):
		return self.name+str(self.birth_day)


class Violation(models.Model):
	class Meta:
		verbose_name = "违规"
		verbose_name_plural	 = "违规"
	car = models.ForeignKey('Car', verbose_name="车辆", on_delete=models.CASCASE,)
	location = models.CharField(max_length=50, verbose_name="违规地点")
	violator = models.ForeignKey('Customer', verbose_name="违规顾客", on_delete=models.CASCASE,)
	date = models.DateField(verbose_name="日期")
	kind = models.CharField(max_length=30, verbose_name="违规类型")
	fine = models.IntegerField(verbose_name="罚款金额")
	points = models.IntegerField(verbose_name="被扣点数")
	note = models.TextField(verbose_name="备注")
	handled = models.BooleanField(verbose_name="是否处理")
	def __str__(self):
		return str(self.car)+'|'+str(self.violator)+'|'+str(self.date)