import { useState } from "react";
import { Text, View, TextInput, Button, StyleSheet } from "react-native";

export default function HomeScreen() {

  const [user, setUser] = useState("");
  const [pickup, setPickup] = useState("");
  const [drop, setDrop] = useState("");
  const [ride, setRide] = useState<any>(null);

  const BASE_URL = "https://ridego-1.onrender.com";

  // 🚖 BOOK RIDE (SAFE VERSION)
  const bookRide = async () => {
    try {
      const res = await fetch(`${BASE_URL}/book-ride/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          user,
          pickup_location: pickup,
          drop_location: drop,
          pickup_lat: 28.6,
          pickup_lon: 77.2,
          drop_lat: 28.7,
          drop_lon: 77.3
        })
      });

      const data = await res.json();

      console.log("🔥 FULL RESPONSE:", data); // DEBUG

      // ✅ SAFE HANDLING
      if (!data) {
        alert("No response from server ❌");
        return;
      }

      if (data.ride) {
        setRide(data.ride);
      } else if (data.id) {
        setRide(data);
      } else {
        alert("Invalid response ❌");
        console.log(data);
      }

    } catch (error) {
      console.log(error);
      alert("Booking failed ❌");
    }
  };

  // 🔄 UPDATE RIDE (SAFE)
  const updateRide = async (endpoint: string) => {
    if (!ride || !ride.id) {
      alert("Ride not ready ❌");
      return;
    }

    try {
      const res = await fetch(`${BASE_URL}/${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ ride_id: ride.id })
      });

      const data = await res.json();

      console.log("🔥 UPDATE RESPONSE:", data);

      setRide(data);

    } catch (error) {
      console.log(error);
      alert("Update failed ❌");
    }
  };

  return (
    <View style={styles.container}>

      <Text style={styles.title}>🚖 RideGo App</Text>

      <TextInput
        placeholder="User ID"
        style={styles.input}
        onChangeText={setUser}
      />

      <TextInput
        placeholder="Pickup Location"
        style={styles.input}
        onChangeText={setPickup}
      />

      <TextInput
        placeholder="Drop Location"
        style={styles.input}
        onChangeText={setDrop}
      />

      <Button title="Book Ride" onPress={bookRide} />

      {/* ✅ SAFE UI */}
      {ride && ride.id && (
        <View style={styles.card}>

          <Text>Status: {ride.status || "N/A"}</Text>
          <Text>Fare: ₹{ride.fare || "N/A"}</Text>

          {ride.message && (
            <Text style={{ color: "red" }}>{ride.message}</Text>
          )}

          {ride.status === "booked" && (
            <Button title="Accept Ride" onPress={() => updateRide("accept-ride/")} />
          )}

          {ride.status === "accepted" && (
            <Button title="Start Ride" onPress={() => updateRide("start-ride/")} />
          )}

          {ride.status === "started" && (
            <Button title="Complete Ride" onPress={() => updateRide("complete-ride/")} />
          )}

        </View>
      )}

    </View>
  );
}

// 🎨 STYLES
const styles = StyleSheet.create({
  container: {
    marginTop: 50,
    padding: 20
  },
  title: {
    fontSize: 22,
    marginBottom: 20
  },
  input: {
    borderWidth: 1,
    marginBottom: 10,
    padding: 10,
    borderRadius: 5
  },
  card: {
    marginTop: 20,
    padding: 15,
    borderWidth: 1,
    borderRadius: 5
  }
});