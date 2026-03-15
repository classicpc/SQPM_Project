curl -X PUT \
http://localhost:8080/api/2/things/org.vehicle:car1 \
-u ditto:ditto \
-H "Content-Type: application/json" \
-d '{
 "attributes": {
   "vehicleId": "car1"
 },
 "features": {
   "telemetry": {
     "properties": {
       "speed": 0
     }
   }
 }
}'
