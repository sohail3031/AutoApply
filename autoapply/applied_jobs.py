class AppliedJobs:
    def __init__(self, id, job_title, company_name, location, salary, description, job_link, source, date_applied) -> None:
        self.id = id
        self.job_title = job_title
        self.company_name=  company_name
        self.location = location
        self.salary = salary
        self.description = description
        self.job_link = job_link
        self.source = source
        self.date_applied = date_applied

    def __str__(self) -> str:
        return (f"Job Detail:\n"
                f"ID: {self.id}\n"
                f"Job Title: {self.job_title}\n"
                f"Company Name: {self.company_name}\n"
                f"Location: {self.location}\n"
                f"Salary: {self.salary}\n"
                f"Job Link: {self.job_link}\n"
                f"Source: {self.source}\n"
                f"Date Applied: {self.date_applied}\n"
                f"Description: {self.description}")
