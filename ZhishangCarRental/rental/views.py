from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import datetime
import json
from datetime import timedelta
from .models import Car
from .models import Reservation
from .models import Customer
from .models import Violation
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
import calendar
import logging
from .forms import StatForm
from .forms import CustomerForm
from .forms import SearchCarForm
from .forms import ViolatorForm

logger=logging.getLogger(__name__)

@login_required
def index(request):
	customers_born_today=Customer.objects.filter(birth_day__month=datetime.date.today().month, birth_day__day=datetime.date.today().day)
	full_car_list=Car.objects.all()
	this_week_reservation = Reservation.objects.filter(endDate__gte=datetime.date.today(), startDate__lte=datetime.date.today()+timedelta(days=7))
	result={}
	for c in full_car_list:
		result[str(c)]=this_week_reservation.filter(car=c)
	context={'car_availability': result,
			 'shouxing': customers_born_today,
			 }
	return render(request, 'rental/index.html', context)


@login_required
def stat(request):
	if request.method == 'POST':
		month=request.POST.__getitem__('month')
		full_car_list=Car.objects.all()
		carNum=full_car_list.count()
		title=''
		result={}
		total=0
		totalDays=0
		if month:			
			nian=month[:4]
			yue=month[4:]
			nianInt=int(nian)
			yueInt=int(yue)
			title=nian+'年'+yue+'月'
			numDays=calendar.monthrange(nianInt,yueInt)[1]
			month_reservations=Reservation.objects.filter(endDate__gt=datetime.date(nianInt,yueInt,1), startDate__lte=datetime.date(nianInt,yueInt,numDays))
			for c in full_car_list:
				logger.debug("car name is: "+str(c))
				amount=0
				days=0
				this_car_reservation=month_reservations.filter(car=c)
				if this_car_reservation.count()==0:
					result[str(c)]=str(amount)+'／无'
					continue
				mid_res=this_car_reservation.filter(endDate__lte=datetime.date(nianInt,yueInt,numDays), startDate__gte=datetime.date(nianInt,yueInt,1))
				midAmount=0
				midDays=0
				for res in mid_res:
					# The total_amount of a reservation is actually daily rate 
					red_days=(res.endDate-res.startDate).days # Stop adding 1 because of customer's request
					midAmount+=res.total_amount*red_days
					midDays+=red_days
				#logger.debug("midays is: "+str(midDays))
				#logger.debug("midAmount is: "+str(midAmount))
				amount+=midAmount
				days+=midDays
				front_res=this_car_reservation.filter(endDate__lte=datetime.date(nianInt,yueInt,numDays), startDate__lt=datetime.date(nianInt,yueInt,1))
				if front_res.count()!=0:
					res=front_res[0]
					includedDays=(res.endDate-datetime.date(nianInt,yueInt,1)).days
					#logger.debug("frontdays is: "+str(includedDays))
					frontAmount=res.total_amount*includedDays
					#logger.debug("frontAmount is: "+str(frontAmount))
					days+=includedDays
					amount+=frontAmount
				end_res=this_car_reservation.filter(endDate__gt=datetime.date(nianInt,yueInt,numDays), startDate__gte=datetime.date(nianInt,yueInt,1))
				if end_res.count()!=0:
					res=end_res[0]
					includedDays=(datetime.date(nianInt,yueInt,numDays)-res.startDate).days+1 # need to +1 for the startDate== last day of the month scenario
					#logger.debug("enddays is: "+str(includedDays))
					endAmount=res.total_amount*includedDays
					#logger.debug("endAmount is: "+str(endAmount))
					days+=includedDays
					amount+=endAmount
				surround_res=this_car_reservation.filter(endDate__gt=datetime.date(nianInt,yueInt,numDays), startDate__lt=datetime.date(nianInt,yueInt,1))
				if surround_res.count()!=0:
					res=surround_res[0]
					#logger.debug("surround res is: "+str(res))
					includedDays=numDays
					#logger.debug("surrdays is: "+str(includedDays))
					days+=includedDays
					amount+=res.total_amount*includedDays
				result[str(c)]=str(amount)+'／'+"{0:.2f}".format(days/numDays)
				total+=amount
				totalDays+=days	
		else:
			title='历史所有'
			all_reservations=Reservation.objects.all()
			for c in full_car_list:
				amount=0
				this_car_reservation=all_reservations.filter(car=c)
				for res in this_car_reservation:
					red_days=(res.endDate-res.startDate).days
					amount+=res.total_amount*red_days
				result[str(c)]=str(amount)+'／无'
				total+=amount
					
		amount_and_percentage=str(total)+'／无' if not month else str(total)+'／'+"{0:.2f}".format(totalDays/numDays/carNum)

		stat_form=StatForm()
		context={'statistics': result,
				'taitou': title,
				'zongji': amount_and_percentage,
				'form': stat_form }
		return render(request, 'rental/stat.html', context)
	else:
		stat_form = StatForm()
		return render(request, 'rental/stat.html', {'form': stat_form})

@login_required
def customer_info(request):
	if request.method == 'POST':
		form = CustomerForm(request.POST)
		if form.is_valid():
			mingzi=form.cleaned_data['name_string']
			selected_customers=Customer.objects.filter(name=mingzi)
			cus_info_list=[]
			indicator='indi'
			for cus in selected_customers:
				cus_info={}
				cus_info['name']=cus.name
				cus_info['id']=cus.ID_number
				cus_reserv=Reservation.objects.filter(customer=cus)
				resNum=cus_reserv.count()
				total_spending=0
				resEntries={}
				for res in cus_reserv:
					duration=(res.endDate-res.startDate).days
					resEntries[res.car.plateName+"／"+str(res.startDate)+'->'+str(res.endDate)]=str(res.total_amount*duration)+"（"+"{0:.2f}".format(res.total_amount)+"／天）"
					total_spending+=res.total_amount*duration
				cus_info['res_entries']=resEntries
				cus_info['res_num']=resNum
				cus_info['to_spending']=total_spending
				cus_violation=Violation.objects.filter(violator=cus)
				vioNum=cus_violation.count()
				vioDict={}
				for vio in cus_violation:
					vioDict[vio.car.plateName+"／"+str(vio.date)+"／"+vio.kind]=str(vio.points)+"／"+str(vio.fine)
				cus_info['vio_entries']=vioDict
				cus_info['vio_number']=vioNum
				cus_info_list.append(cus_info)
				

			customer_form=CustomerForm() # Need to put this in the context to display the form
			context={'customer_info_list': cus_info_list,
					'ind':indicator,
					'form': customer_form }
			return render(request, 'rental/customer.html', context)
	else:
		customer_form = CustomerForm()
		return render(request, 'rental/customer.html', {'form': customer_form})

@login_required
def available_cars(request):
	if request.method == 'POST':
		form = SearchCarForm(request.POST)
		if form.is_valid():
			start=datetime.datetime.strptime(form.cleaned_data['start'], "%Y%m%d")
			end=datetime.datetime.strptime(form.cleaned_data['end'], "%Y%m%d")
			full_car_list=Car.objects.all()
			avai_car_set=set(full_car_list)
			period_reservations = Reservation.objects.filter(endDate__gte=start, startDate__lte=end)
			taken_car_list=set()		
			for res in period_reservations:
				taken_car_list.add(res.car)
			avai_car_set-=taken_car_list
			search_car_form=SearchCarForm()
			context={'start_date': start,
					 'end_date': end,
					 'car_list': avai_car_set,
					 'form': search_car_form
					 }
			return render(request, 'rental/available_cars.html', context)
	# if a GET (or any other method) we'll create a blank form
	else:
		search_car_form = SearchCarForm()
		return render(request, 'rental/available_cars.html', {'form': search_car_form})

@login_required
def violator(request):
	if request.method == 'POST':
		form = ViolatorForm(request.POST)
		if form.is_valid():
			date=datetime.datetime.strptime(form.cleaned_data['date'], "%Y%m%d")
			plate=form.cleaned_data['plate']
			vio_reservations = Reservation.objects.filter(endDate__gte=date, startDate__lte=date, car__plateName__exact=plate)
			vio_form=ViolatorForm()
			context={'riqi': date,
					 'paizhao': plate,
					 'res_list': vio_reservations,
					 'form': vio_form
					 }
			return render(request, 'rental/violator.html', context)
	# if a GET (or any other method) we'll create a blank form
	else:
		vio_form = ViolatorForm()
		return render(request, 'rental/violator.html', {'form': vio_form})


