app.get("/user-data", authorized, async (req, res, next) => {
  let title = req.header("token").startsWith("admin") ? "admin" : "user";
  if (title == "admin") {
    res.status(400).json({
      message: "Not a user"
    });
  } else {
    const db = await dbPromise;
    let resdb = await db.get(
      "SELECT * FROM users WHERE username = ?",
      // CHANGED: use only the username associated with the authenticated token.
      tokensUsername[req.header("token")]
    );
    res.json({
      username: resdb.user,
      email: resdb.email,
      address: resdb.address,
      phone: resdb.phone,
      salary: resdb.salary
    });
  }
});
