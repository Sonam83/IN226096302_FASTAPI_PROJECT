from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field

app=FastAPI() 

# ________________________________ Pydantic Models for validation _____________________________
# ___________________________ Q6 : Booking Request ______________________________________-
class BookingRequest(BaseModel):
    customer_name:str=Field(...,min_length=2)
    movie_id:int=Field(...,gt=0)
    seats:int=Field(...,gt=0,le=10)
    phone:str=Field(...,min_length=10)
    seat_type:str=Field('standard')  # standard/premium/recliner
    promo_code:str=Field('',description='Optional promo code')

# ____________________ Q11: New movies post - basemodel __________________________________
class NewMovie(BaseModel):
    title:str=Field(...,min_length=2)
    genre:str=Field(...,min_length=2)
    language:str=Field(...,min_length=2)
    duration_mins:int=Field(...,gt=0)
    ticket_price:int=Field(...,gt=0)
    seats_available:int=Field(...,gt=0)

# ____________________________ Q14 : Seat hold request model _________________________
class SeatHoldRequest(BaseModel):
    customer_name:str=Field(...,min_length=2)
    movie_id:int=Field(...,gt=0)
    seats:int=Field(...,gt=0,le=10)

# ======================== Data of Movies ==============================

movies=[{'id':1,'title':'Inception','genre':'Action','language':'English','duration_mins':148,'ticket_price':250,'seats_available':50},
        {'id':2, 'title':'3 Idiots','genre':'Drama', 'language':'Hindi','duration_mins':170,'ticket_price':200,'seats_available':60},
    {'id':3,'title':'The Conjuring','genre':'Horror','language':'English','duration_mins':112,'ticket_price':220,'seats_available':40},
    {'id':4,'title':'Jathi Ratnalu','genre':'Comedy','language':'Telugu','duration_mins':145,'ticket_price':180,'seats_available':70},
    {'id':5,'title':'Avengers',     'genre':'Action','language':'English','duration_mins':160,'ticket_price':300,'seats_available':30},
    {'id':6,'title':'Drishyam',     'genre':'Drama','language':'Malayalam','duration_mins':140,'ticket_price':190,'seats_available':55},
]

bookings=[]
booking_counter=1
holds=[]
hold_counter=1

# ______________________________ Helper Functions ___________________________________
def find_movie(movie_id:int): #Q3
    for m in movies:
        if m['id']==movie_id:
            return m 
    return None

def calculate_ticket_cost(base_price:int,seats:int,seat_type:str,promo_code:str): #Q7


    '''seat multiplier
    if seat_type=='premium':
        multiplier=1.5
    elif seat_type=='recliner':
        multiplier=2
    else:
        multiplier=1

    original_cost=base_price*seats*multiplier'''

    #step 1: seat type multiplier
    seat_type=seat_type.lower()

    if seat_type=='premium':
        multiplier=1.5
    elif seat_type=='recliner':
        multiplier=2
    else:
        multiplier=1

    #step 2: calculate original cost
    original_cost=base_price*seats*multiplier

    #step 3 : Apply promo
    promo_code=promo_code.upper()

    #promo discount
    discount=0
    if promo_code=='SAVE10':
        discount=0.10
    elif promo_code=='SAVE20':
        discount=0.20

    discounted_cost=original_cost*(1-discount)

    return { 
        'original_cost':int(original_cost),
        'discounted_cost':int(discounted_cost),
        'discount_applied':f"{int(discount*100)}%"
    }

def filter_movies_logic(genre=None,language=None,max_price=None,min_seats=None):
    result=movies

    if genre is not None:
        result=[m for m in result if m['genre'].lower()==genre.lower()]

    if language is not None:
        result=[m for m in result if m['language'].lower()==language.lower()]

    if max_price is not None:
        result=[m for m in result if m['ticket_price']<=max_price]

    if min_seats is not None:
        result=[m for m in result if m['seats_available']>=min_seats]

    return result
 

# ======================== Endpoints ===================================
# __________________________ Q1 : Home page ______________________________
@app.get('/')
def home():
    return {'message':'Welcome to CineStar Booking'}

# _____________________________ Q2 : get movies data, total , total seats available ______________________
@app.get('/movies')
def get_all_movies():
    total_seats=sum(m['seats_available'] for m in movies)
    return {
        'movies':movies,
        'total' : len(movies),
        'total_seats_available' : total_seats
    }

# __________________________________ Q10 : Filter movies ______________________________________-
@app.get('/movies/filter')
def filter_movies(
    genre:str=Query(None),
    language:str=Query(None),
    max_price:int=Query(None),
    min_seats:int=Query(None),):

    result=filter_movies_logic(genre,language,max_price,min_seats)

    if not results:
        return {
            'message':'No movies found with given filters',
            'filters_applied':{
                'genre':genre,
                'language':language,
                'max_price':max_price,
                'min_seats':min_seats
            }
        }

    return {
        'filters_applied':{
            'genre':genre,
            'language':language,
            'max_price':max_price,
            'min_seats':min_seats
        },
        'total_found':len(result),
        'movies':result
    }

# _______________________________ Q11 : Add movie __________________________________________________
@app.post('/movies')
def add_movie(new_movie:NewMovie,response:Response):
    #duplicate title check
    existing_titles=[m['title'].lower() for m in movies]

    if new_movie.title.lower() in existing_titles:
        response.status_code=status.HTTP_400_BAD_REQUEST
        return {'error':'Movie with this title already exists'}

    next_id=max(m['id'] for m in movies) + 1

    movie={
        'id':next_id,
        'title':new_movie.title,
        'genre':new_movie.genre,
        'language':new_movie.language,
        'duration_mins':new_movie.duration_mins,
        'ticket_price':new_movie.ticket_price,
        'seats_available':new_movie.seats_available
    }

    movies.append(movie)

    response.status_code=status.HTTP_201_CREATED

    return {
        'message':'Movie Added Successfully',
        'movie':movie
    }


# _________________________________ Q5 : Movies Summary _________________________________________
@app.get('/movies/summary')
def movies_summary():
    prices=[m['ticket_price'] for m in movies]
    genre_count={}
    for m in movies:
        genre_count[m['genre']] = genre_count.get(m['genre'],0)+1

    return {
        'total_movies':len(movies),
        'most_expensive_ticket':max(prices), 
        'cheapest_ticket':min(prices),
        'total_seats':sum(m['seats_available'] for m in movies),
        'movies_by_genre':genre_count
    }

# ______________________________________ Q16: Movies search _____________________________________-
@app.get('/movies/search')
def search_movies(
    keyword:str=Query(...,description='Search by title, genre, or language')):

    keyword=keyword.lower()

    results=[m for m in movies if keyword in m['title'].lower() or keyword in m['genre'].lower() or keyword in m['language'].lower()]

    if not results:
        return {
            'message':f'No movies found for keyword: {keyword}',
            'results':[]
        }

    return {
        'keyword':keyword,
        'total_found':len(results),
        'movies':results
    }

# ________________________________________________ Q17:Sort movies_____________________________________
@app.get('/movies/sort')
def sort_movies(sort_by:str=Query('ticket_price'),order:str=Query('asc')):
    valid_fields=['ticket_price','title','duration_mins','seats_available']

    if sort_by not in valid_fields:
        return {'error':f'sort_by must be one of {valid_fields}'}

    if order not in ['asc','desc']:
        return {'error':"order must be 'asc' or 'desc'"}

    sorted_movies=sorted(movies,key=lambda m:m[sort_by],reverse=(order=='desc'))

    return {
        'sort_by':sort_by,
        'order':order,
        'movies':sorted_movies
    }

# ________________________________________________ Q18 : Movies page __________________________________-
@app.get('/movies/page')
def paginate_movies(page:int=Query(1,ge=1),limit:int=Query(3,ge=1,le=20)):
    start=(page-1)*limit
    end=start+limit
    paged=movies[start:end]

    return {
        'page':page,
        'limit':limit,
        'total':len(movies),
        'total_pages':-(-len(movies)//limit),
        'movies':paged
            }

# __________________________ Q20:Browse movies : combine search,filter,sort,pagination_______________________-
@app.get('/movies/browse')
def browse_movies(keyword:str=Query(None),
   genre:str=Query(None),language:str=Query(None),sort_by:str=Query('ticket_price'),order:str=Query('asc'),
    page:int=Query(1,ge=1),limit:int=Query(3,ge=1,le=20)):

    result=movies

    #keyword search
    if keyword:
        keyword=keyword.lower()
        result=[m for m in result if keyword in m['title'].lower() or keyword in m['genre'].lower() or keyword in m['language'].lower()]

    #filter
    if genre:
        result=[m for m in result if  m['genre'].lower()==genre.lower()]

    if language:
        result=[m for m in result if  m['language'].lower()==language.lower()]

    # sort
    valid_fields=['ticket_price','title','duration_mins','seats_available']

    if sort_by in valid_fields:
        result=sorted(result,key=lambda m:m[sort_by],reverse=(order=='desc'))

        
    # pagination
    total=len(result)
    start=(page-1)*limit
    paged=result[start:start+limit]

    return {
        'filters':{
            'keyword':keyword,
            'genre':genre,
            'language':language,
            'sort_by':sort_by,
            'order':order,
            'page':page,
            'limit':limit
        },
        'total_found':total,
        'total_pages':-(-total//limit),
        'movies':paged
    }

# __________________________ Q3 : get movies by id _________________________________________________-
@app.get('/movies/{movie_id}')
def get_movie(movie_id:int):
    movie=find_movie(movie_id)
    if not movie:
        return {'error':'Movie not found'}
    return {'movie':movie}

# _________________________________ Q12 : Update movies __________________________________________
@app.put('/movies/{movie_id}')
def update_movie(
    movie_id:int,
    response:Response,
    ticket_price:int=Query(None,gt=0),
    seats_available:int=Query(None,ge=0),):

    movie=find_movie(movie_id)

    if not movie:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {'error':'Movie Not Found'}

    if ticket_price is not None:
        movie['ticket_price']=ticket_price

    if seats_available is not None:
        movie['seats_available']=seats_available

    return {
        'message':'Movie updated Successfully',
        'movie':movie
    }

# ____________________________________ Q13 : Delete Movie ____________________________________-
@app.delete('/movies/{movie_id}')
def delete_movie(movie_id:int,response:Response):
    movie=find_movie(movie_id)

    if not movie:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {'error':'Movie Not found'} 

    for booking in bookings:
        if booking['movie_id']==movie_id:
            response.status_code=status.HTTP_400_BAD_REQUEST
            return {
                'error':'Cannot delete movie with existing bookings'
            }

    movies.remove(movie)

    return {
        'message':f"Movie '{movie['title']}' deleted successfully"
    }

# ________________________________ Q4 : get all bookings __________________________________________-
@app.get('/bookings')
def get_all_bookings():
    total_revenue=sum(b['total_cost'] for b in bookings) if bookings else 0
    return {
        'bookings':bookings,
        'total':len(bookings),
        'total_revenue':total_revenue
    }

# _________________________________ Q8 & Q9 : to post bookings ____________________________________-----
@app.post('/bookings')
def create_booking(booking:BookingRequest):
    global booking_counter
    movie=find_movie(booking.movie_id)

    #check movie
    if not movie:
        return {'error':'Movie not found'}

    #check seats
    if booking.seats>movie['seats_available']:
        return {'error':'Not enough seats available',
        'available_seats':movie['seats_available']}

    #calculate cost
    cost=calculate_ticket_cost(
        base_price=movie['ticket_price'],
        seats=booking.seats,
        seat_type=booking.seat_type,
        promo_code=booking.promo_code
        #movie['ticket_price'],booking.seats,booking.seat_type,booking.promo_code
    )

    #reduce seats
    movie['seats_available'] -= booking.seats

    # create booking
    new_booking={
        'booking_id':booking_counter,
        'customer_name':booking.customer_name,
        'movie_id':booking.movie_id,
        'movie_title':movie['title'],
        'seats':booking.seats,
        'seat_type':booking.seat_type,
        'phone':booking.phone,
        'original_cost':cost['original_cost'],
        'discounted_cost':cost['discounted_cost'],
        'discount_applied':cost['discount_applied']
    }

    bookings.append(new_booking)
    booking_counter+=1

    return {
        'message':'Booking Confirmed Successfully',
        'booking':new_booking
    }

# ___________________________- Q19 - Booking search on customer name ____________________________________-
@app.get('/bookings/search')
def search_bookings(customer_name:str=Query(...)):
    results=[b for b in bookings if customer_name.lower() in b['customer_name'].lower()]

    if not results:
        return {'message':f'No bookings found for {customer_name}'}

    return {
        'customer_name':customer_name,
        'total_found':len(results),
        'bookings':results
    }

# _____________---booking sort_____________________________
@app.get('/bookings/sort')
def sort_bookings(sort_by:str=Query('discounted_cost'),order:str=Query('asc')):
    valid_fields=['discounted_cost','seats']

    if sort_by not in valid_fields:
        return {'error':f'sort_by must be one of {valid_fields}'}

    if order not in ['asc','desc']:
        return {'error':"order must be 'asc' or 'desc'"}

    sorted_data=sorted(bookings,key=lambda b:b[sort_by],reverse=(order=='desc'))

    return {
        'sort_by':sort_by,
        'order':order,
        'movies':sorted_data
    }

# ___________________- get bookings page ____________________________________
@app.get('/bookings/page')
def paginate_bookings(page:int=Query(1,ge=1),limit:int=Query(3,ge=1,le=20)):
    start=(page-1)*limit
    
    return {
        'page':page,
        'limit':limit,
        'total':len(bookings),
        'total_pages':-(-len(bookings)//limit),
        'bookings':bookings[start:start+limit]
            }

# _____________________________- Q14 : Seat hold ___________________________________________
@app.post('/seat-hold')
def create_seat_hold(hold:SeatHoldRequest):
    global hold_counter

    movie=find_movie(hold.movie_id) 

    if not movie :
        return {'error':'Movie not found'}

    if hold.seats>movie['seats_available']:
        return {
            'error':'Not enough seats available',
            'available_seats':movie['seats_available']
        }

    # step : temporarily reducing seats
    movie['seats_available']-=hold.seats 

    # step : create hold entry
    hold_entry={
        'hold_id':hold_counter,
        'customer_name':hold.customer_name,
        'movie_id':hold.movie_id,
        'movie_title':movie['title'],
        'seats':hold.seats,
        'status':'held'
    }

    holds.append(hold_entry) 
    hold_counter+=1

    return {
        'message':'Seats held successfully',
        'hold':hold_entry
    }

# To view all holds
@app.get('/seat-hold')
def get_all_holds():
    return {
        'holds':holds,
        'total_holds':len(holds)
    }

# __________________________________- Q15 : Confirm seat hold___________________________-
@app.post('/seat-confirm/{hold_id}')
def confirm_seat_hold(hold_id:int):
    global booking_counter

    # final hold
    hold=None
    for h in holds:
        if h['hold_id']==hold_id:
            hold=h
            break

    if not hold:
        return {'error':'Hold not found'} 

    # create booking from hold
    movie=find_movie(hold['movie_id'])

    total_cost=hold['seats']*movie['ticket_price']

    booking={
        'booking_id':booking_counter,
        'customer_name':hold['customer_name'],
        'movie_id':hold['movie_id'],
        'movie_title':hold['movie_title'],
        'seats':hold['seats'],
        'seat_type':'standard',
        'original_cost':total_cost,
        'discounted_cost':total_cost,
        'status':'confirmed'
    }

    bookings.append(booking)
    booking_counter+=1

    # remove hold
    holds.remove(hold)

    return {
        'message':'Booking confirmed from hold',
        'Booking':booking
    }

#_______________--Release seat hold_______________________
@app.delete('/seat-release/{hold_id}')
def release_seat_hold(hold_id:int):

    # find hold
    hold=None
    for h in holds:
        if h['hold_id']==hold_id:
            hold=h
            break

    if not hold:
        return {'error':'Hold not found'} 

    # restore seats
    movie=find_movie(hold['movie_id'])
    movie['seats_available']+=hold['seats'] 

    # remove hold
    holds.remove(hold)

    return {
        'message':'Seat Hold Released Successfully',
        'released_seats':hold['seats']
    }

