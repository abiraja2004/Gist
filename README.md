Gist
==============
Online goods and services sometimes can have hundreds or even thousands of reviews. Reading reviews can be a tedious task so often times we look to the number of stars a good or service has but that doesn't convey a whole lot of information. Gist is designed to summarize reviews by picking out key points from customers' reviews and displaying them to the user.   

## How do we find key points?
Each sentence in every review is a potential key point and is scored on the following attributes using a gaussian function for each attribute
 - Sentiment<br />
    We would like to grab reviews that best match how most customers feel about a product or service. If they feel 'meh' about it then we want to grab parts of reviews that have a 'meh' feeling. 
 - Relevance<br />
    How does this statement relate to the product or service? TF-IDF is used to calculate key terms which we most likely would like to include in our summarization. Ex. Rice would be a key term for a sushi restaurant therefore we would rank sentences including the term rice higher than those that don't contain rice. 
 - Sentence Length<br />
    The length of a sentence can tell us how much information that sentence may contain. "The pasta was bomb" may tell us that the customer was enthusiastic with their meal but it doesn't convey a whole lot compared to "the amount of garlic they use in their pasta sauce creates a perfect balance of flavors." The optimal sentence length which we compare each sentence to is based upon Yelp's elite reviews.   

After each sentence is scored on each attribute the top N sentences are calculated using genetic algorithms. A sentence's fitness is calculated by using a weighted sum of the attribute scores.

## Scalability
Information on reviews is scraped directly from the website. Scraping can be a lengthy process when there is a lot of information to grab; requesting large amounts of information can look like a denial of service. Because of this we want to limit the amount of real time summarizations by performing lazy evaluations. All results are stored in the database therefore whenever a review has already been summarized we can pull up the results. If the results are "stale" then we re-summarize. This is particularly important with services as their quality may change over time. 

Although our summarization algorithm is designed to work with any type of review, a web scraper or api must be implemented to support each and every website where we would like to summarize reviews. Currently supported websites are yelp and metacritic. 



Note: This is not a commercial product and was created for educational purposes under the fair use act
