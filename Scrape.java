// Author: Sandeep Thangirala
// Download JSoup 
// Thanks to "https://github.com/NobodyWHU/Leetcode"

import java.io.IOException;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class Scrape {
	
	public static void main(String args[]){
		try {
				Document doc = Jsoup.connect("https://github.com/NobodyWHU/Leetcode").get();
				String title = doc.title();
			    Elements links = doc.select("a[href]");
			    for (Element link : links) {
			    	if(link.attr("href").contains("/tree/master/"))
			    		getData("https://github.com"+link.attr("href"));
			    }
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	public static void getData(String link) throws IOException{
		
		Document doc = Jsoup.connect(link).get();
		Elements links = doc.select("a[href]");
		for (Element Qlink : links) {
	        if(Qlink.text().contains("Question")){
	        	getCompany("https://github.com"+Qlink.attr("href"));
	        }
	    }
	}
	
public static void getCompany(String link) throws IOException{		
		Document doc = Jsoup.connect(link).get();
		Elements links = doc.select("a[href]");
		for (Element Clink : links) {
	        if(Clink.text().contains("Original Page")){
	        	System.out.println("\nOriginal Page: " + Clink.attr("href"));
	        }
	        if(Clink.attr("href").contains("/NobodyWHU/Leetcode/blob/master/company/")){
	        	System.out.print(" "+ Clink.text());
	        }
	      }		
		System.out.println("\n"+"===========");
	}
}
