This was from our ANC script but we don't need it right now.


  # Add quarterly financial report URLs from Luke's CSV file.
  # Warning: Historical information may not correspond to current ANCs if they
  # were renamed after 2012 redistricting.
  s3_data = urlopen("https://s3.amazonaws.com/dcanc/index.csv")
  for rec in csv.DictReader(s3_data):
    try:
      anc = output[rec["ANC"][0]]["ancs"][rec["ANC"][1]]
    except KeyError:
      # ANC no longer exists after redistricting.
      continue
    anc.setdefault("quarterly_financial_report_pdf_url", []).append(
      {
        "fiscal_year": rec["FY"],
        "quarter": rec["quarter"],
        "url": "https://s3.amazonaws.com/dcanc/" + rec["filename"],
        "size": rec["size"],
        "pages": rec["pages,"],
      })
    

