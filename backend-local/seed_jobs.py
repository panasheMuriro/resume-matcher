from embedding_utils import insert_job

jobs_to_seed = [
    (
        'Frontend Developer',
        'We are looking for a skilled Frontend Developer proficient in React, TypeScript, and Tailwind CSS. '
        'The ideal candidate should have experience building responsive and interactive UIs, working with REST APIs, '
        'and optimizing web performance.'
    ),
    (
        'Backend Engineer',
        'Seeking a Backend Engineer with strong experience in Node.js, Express, and PostgreSQL. '
        'Responsibilities include designing scalable APIs, integrating third-party services, and ensuring data integrity. '
        'Experience with cloud platforms like AWS or GCP is a plus.'
    ),
    (
        'Data Analyst',
        'Join our team as a Data Analyst to turn raw data into actionable insights. '
        'Must be skilled in SQL, Excel, and Python for data analysis. Experience with BI tools like Tableau or Power BI is preferred. '
        'Strong statistical knowledge is an advantage.'
    ),
    (
        'DevOps Engineer',
        'Looking for a DevOps Engineer experienced with CI/CD pipelines, Docker, Kubernetes, and cloud infrastructure. '
        'Must have experience with monitoring tools and automating deployments. Familiarity with Terraform is beneficial.'
    ),
    (
        'Mobile App Developer',
        'We need a Mobile App Developer proficient in Flutter or React Native. '
        'Should have experience building cross-platform mobile apps, integrating APIs, and managing app store deployments. '
        'Knowledge of mobile UI/UX best practices is important.'
    )
]

for title, desc in jobs_to_seed:
    insert_job(title, desc)
    print(f"Inserted job: {title}")
