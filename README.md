# python-exec-api

## Setup:
```
git clone https://github.com/YOUR_USERNAME/python-exec-api.git
cd python-exec-api
```

## Build and Run Locally:
```
docker build -t python-execution-api .
```
After the Docker image is created, run->
```
docker run -p 8080:8080 python-execution-api
```
## Testing:
The following are curl examples for locally testing->
```
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return \"Hello from inside nsjail!\""
}'
```
output for the above-


![image](https://github.com/user-attachments/assets/02b4a3e7-ff05-4f78-8a86-a1374eab602a)

Example with pandas-
```
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "import pandas as pd\n\ndef main():\n    df = pd.DataFrame({\"A\": [1, 2], \"B\": [3, 4]})\n    print(df.to_string(index=False))\n    return {\"sum\": int(df[\"A\"].sum() + df[\"B\"].sum())}"
}'
```
output for the above-

![image](https://github.com/user-attachments/assets/0d9b74c7-d15f-4494-99dc-0fe424373835)


## Project Structure
```
├─ app.py               # Flask API to handle validation & sandboxed execution
├─ nsjail.cfg           # NSJail configuration file
├─ Dockerfile           # Docker setup for Python + NSJail
├─ requirements.txt     # Python dependencies
├─ README.md            # Project documentation
```

## Deploying on Google Cloud Run
I did try to run it on Google Cloud Run, but unfortunately, I was stuck with a complication:

The following are the steps I followed for deploying->
```
gcloud builds submit --tag gcr.io/PROJECT_ID/python-nsjail-api

gcloud run deploy python-nsjail-api \
  --image gcr.io/PROJECT_ID/python-nsjail-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```
Testing->

```
curl -X POST https://python-nsjail-api-493291479527.us-central1.run.app/execute   -H "Content-Type: application/json"   -d '{
    "script": "def main():\n    return \"Hello from inside nsjail!\""
}'
```
![clouddeploy](https://github.com/user-attachments/assets/eead980f-2045-42d0-81ab-15654a87e214)

It kept returning the httpRequest.status: 500

I tried multiple times to redeploy with minimal nsjail.cfg for Cloud Run and kept facing an Internal Server Error. Same as the above image.

## Possible reasons for successfully deploying->
```
1. Cloud Run doesn’t allow privileged containers.
2. Cloud Run uses gVisor-based sandboxing, which restricts many low-level system operations. 
3. Cannot mount /dev, /proc, or other special paths.
4. NSJail fails silently if these are not available or writable.
```

## Possible workarounds:
```
1. Extremely minimal `nsjail.cfg` file
2. Use Compute Engine VM / GKE for full isolation
```










