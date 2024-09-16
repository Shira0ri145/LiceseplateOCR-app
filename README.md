# LiceseplateOCR-app

choice 1). run docker image

-- Step 1 : docker build -t fast-lpocr-app .                                    
Check : Docker images                                                                   
-- Step 2 : docker run -d --name fast-lpocr-appcontainer -p 8000:8000 fast-lpocr-app                        

choice 2). run docker-compose (recommended for who want to install pgadmin4 and postgreSQL)