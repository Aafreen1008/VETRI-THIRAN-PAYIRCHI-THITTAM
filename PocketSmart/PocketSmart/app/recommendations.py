from urllib.parse import quote_plus

PLATFORMS = {
    "amazon": "https://www.amazon.in/s?k=",
    "flipkart": "https://www.flipkart.com/search?q=",
    "google": "https://www.google.com/search?q=",
}

def links(term: str) -> dict[str, str]:
    q = quote_plus(term)
    return {name: url + q for name, url in PLATFORMS.items()}

def clamp_budget(items, budget):
    total = sum(float(x.get("estimated_cost", 0)) for x in items)
    if total <= budget:
        return items
    factor = budget / total if total else 1
    for x in items:
        x["estimated_cost"] = round(float(x.get("estimated_cost", 0)) * factor, 2)
    return items

def fallback_home(data):
    b = data.total_budget
    items = []
    if data.num_lights:
        items.append({"name":"LED lighting fixtures","category":"Lighting","quantity":data.num_lights,"estimated_cost":min(b*.12, 1800*data.num_lights),"search_terms":"LED ceiling light India"})
    if data.num_fans:
        items.append({"name":"Energy-efficient ceiling fans","category":"Fans","quantity":data.num_fans,"estimated_cost":min(b*.20, 3500*data.num_fans),"search_terms":"energy efficient ceiling fan India"})
    if data.num_furniture:
        items.append({"name":"Functional furniture","category":"Furniture","quantity":data.num_furniture,"estimated_cost":min(b*.30, 8000*data.num_furniture),"search_terms":"budget home furniture India"})
    if data.num_dining_tables:
        items.append({"name":"Compact dining table","category":"Dining","quantity":data.num_dining_tables,"estimated_cost":min(b*.18, 10000*data.num_dining_tables),"search_terms":"compact dining table India"})
    items = clamp_budget(items,b)
    for x in items: x["shopping_links"] = links(x["search_terms"])
    used=sum(x["estimated_cost"] for x in items)
    return {"summary":"A practical starter plan that keeps the requested quantities within the stated budget.","budget":b,"budget_breakdown":items,"remaining_budget":round(max(0,b-used),2),"tips":["Prioritize essential pieces first.","Measure rooms before buying furniture.","Keep a small buffer for delivery and installation."]}

def fallback_party(data):
    b=data.total_budget; n=data.guest_count
    items=[]
    if data.venue_required: items.append({"name":"Simple venue","category":"Venue","quantity":1,"estimated_cost":min(b*.30, max(2000,n*250)),"search_terms":"budget event venue India"})
    if data.food_required: items.append({"name":"Food and refreshments","category":"Food","quantity":n,"estimated_cost":min(b*.35, max(1500,n*250)),"search_terms":"party catering food India"})
    if data.decoration_required: items.append({"name":"Basic decorations","category":"Decorations","quantity":1,"estimated_cost":min(b*.15, max(800,n*60)),"search_terms":"birthday party decorations India"})
    if data.photography_required: items.append({"name":"Event photography","category":"Photography","quantity":1,"estimated_cost":min(b*.12,5000),"search_terms":"budget event photographer India"})
    items=clamp_budget(items,b)
    for x in items: x["shopping_links"]=links(x["search_terms"])
    used=sum(x["estimated_cost"] for x in items)
    return {"summary":f"A {data.event_type} plan for {n} guests with the requested services.","budget":b,"budget_breakdown":items,"remaining_budget":round(max(0,b-used),2),"tips":["Confirm venue capacity and inclusions before paying.","Compare per-person food pricing.","Keep a contingency amount for last-minute needs."]}

def fallback_jewelry(data):
    b=data.total_budget
    options=[
        {"name":f"Minimal {data.jewelry_type}","category":"Everyday","estimated_cost":round(b*.30,2),"search_terms":f"minimal {data.jewelry_type} {data.material_preference}"},
        {"name":f"Statement {data.jewelry_type}","category":"Occasion","estimated_cost":round(b*.45,2),"search_terms":f"statement {data.jewelry_type} {data.material_preference}"},
        {"name":"Simple accessory set","category":"Set","estimated_cost":round(b*.20,2),"search_terms":f"{data.material_preference} jewellery set"},
    ]
    for x in options:x["shopping_links"]=links(x["search_terms"])
    used=sum(x["estimated_cost"] for x in options)
    return {"summary":f"Options for {data.occasion} using {data.material_preference}.","budget":b,"budget_breakdown":options,"remaining_budget":round(max(0,b-used),2),"tips":["Check material details and return policy.","Choose pieces that match outfits you already own.","Avoid spending the entire budget on one item unless that is intentional."]}
