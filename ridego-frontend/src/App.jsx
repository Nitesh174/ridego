import { useState } from "react";

function App() {

  const [form, setForm] = useState({
    user: "",
    pickup_location: "",
    drop_location: "",
    pickup_lat: "",
    pickup_lon: "",
    drop_lat: "",
    drop_lon: ""
  });

  const [ride, setRide] = useState(null);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  // ✅ FIXED BOOK RIDE
  const bookRide = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/book-ride/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });

      const data = await res.json();

      console.log("BOOK RESPONSE:", data); // 🔥 DEBUG

      // ✅ important fix
      setRide(data.ride || data);

    } catch (error) {
      console.error("ERROR:", error);
      alert("Backend connect nahi ho raha ❌");
    }
  };

  // ✅ FIXED UPDATE RIDE
  const updateRide = async (url) => {
    try {
      const res = await fetch(`"http://localhost:8000/book-ride/"${url}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ride_id: ride.id })
      });

      const data = await res.json();

      console.log("UPDATE RESPONSE:", data); // 🔥 DEBUG

      setRide(data);

    } catch (error) {
      console.error("ERROR:", error);
    }
  };

  return (
    <div className="container mt-5">

      <h1 className="text-center mb-4">🚖 RideGo App</h1>

      {/* FORM */}
      <div className="card p-4 shadow mb-4">
        <h4>Book Ride</h4>

        <input className="form-control mb-2" name="user" placeholder="User ID (e.g. 1)" onChange={handleChange} />

        <input className="form-control mb-2" name="pickup_location" placeholder="Pickup Location" onChange={handleChange} />
        <input className="form-control mb-2" name="drop_location" placeholder="Drop Location" onChange={handleChange} />

        <input className="form-control mb-2" name="pickup_lat" placeholder="Pickup Lat (28.6)" onChange={handleChange} />
        <input className="form-control mb-2" name="pickup_lon" placeholder="Pickup Lon (77.2)" onChange={handleChange} />

        <input className="form-control mb-2" name="drop_lat" placeholder="Drop Lat (28.7)" onChange={handleChange} />
        <input className="form-control mb-2" name="drop_lon" placeholder="Drop Lon (77.3)" onChange={handleChange} />

        <button className="btn btn-primary w-100" onClick={bookRide}>
          Book Ride
        </button>
      </div>

      {/* RIDE DETAILS */}
      {ride && (
        <div className="card p-4 shadow">
          <h4>Ride Details</h4>

          <p><b>Status:</b> {ride.status || "N/A"}</p>
          <p><b>Fare:</b> ₹{ride.fare || "N/A"}</p>

          {/* 🔥 NO DRIVER CASE */}
          {ride.message && (
            <p style={{ color: "red" }}>{ride.message}</p>
          )}

          <div className="d-flex gap-2">

            {ride.status === "booked" && (
              <button className="btn btn-success" onClick={() => updateRide("accept-ride/")}>
                Accept Ride
              </button>
            )}

            {ride.status === "accepted" && (
              <button className="btn btn-warning" onClick={() => updateRide("start-ride/")}>
                Start Ride
              </button>
            )}

            {ride.status === "started" && (
              <button className="btn btn-danger" onClick={() => updateRide("complete-ride/")}>
                Complete Ride
              </button>
            )}

          </div>
        </div>
      )}

    </div>
  );
}

export default App;