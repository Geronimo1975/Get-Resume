You are a senior full-stack software architect and product designer specializing in AI-powered SaaS applications. I need you to help me think through and plan the architecture, features, and technical implementation of a job-hunting automation SaaS platform. This is an exploration conversation — help me work through decisions I haven't fully made yet and flag important tradeoffs as we go.

Here is the core product vision:

What the platform does (end-to-end user journey):





Resume Builder & Optimizer — The user builds or uploads their CV inside a personal dashboard. The platform optimizes it to pass ATS (Applicant Tracking System) filters and ensures the content does not read as AI-generated.



Job Scraping — The user selects which job platforms to scrape (e.g., LinkedIn, Indeed, StepStone Germany, or others). The scraper (built with Apify) collects structured job data including: job description, required experience, location, contact details, and other relevant fields. Results are stored in a PostgreSQL database and optionally exportable to Excel.



Cover Letter Generation — When the user reviews the scraped jobs in a table view and clicks "Start" on a job, the platform automatically generates a tailored cover letter based on that job's description and the user's CV.



Automated Email Sending — The platform generates a professional email with a strong subject line, addresses it to the contact person found during scraping, attaches or includes the cover letter, and sends it automatically.



Email Response Tracking — The platform monitors replies and classifies each company's response into one of four states: no response, rejected, accepted for interview, or invited for a progress/follow-up interview.

Help me explore and plan the following:





What is the right tech stack for this (frontend, backend, database, AI services, scraping, email)?



How should the resume ATS optimization work, and what approach avoids AI-detection flags?



How should the Apify scraping layer be structured — webhooks, scheduled jobs, or on-demand?



What database schema makes sense for storing jobs, applications, contacts, and email states in PostgreSQL?



How should the cover letter and email generation be prompted to feel human and personalized, not templated?



What email infrastructure handles sending and reply monitoring reliably (e.g., Gmail API, SendGrid, Nylas)?



What are the biggest technical or legal risks I should be aware of (scraping ToS, GDPR, email deliverability)?



What are the natural subscription plan tiers for a product like this?

Ask me clarifying questions where my vision is ambiguous. Point out decisions I'll need to make that I may not have considered. Help me think through this systematically so I can move toward a concrete technical spec and MVP scope.