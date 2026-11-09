app.get("/vulnerable", async (req, res, next) => {
  const db = await dbPromise;
  let ret;
  try {
    ret = await db.get(
      "SELECT username FROM users WHERE username = ?",
      req.query.q
    );
  } catch (err) {
    ret = "error";
  }
  res.send(ret);
});
