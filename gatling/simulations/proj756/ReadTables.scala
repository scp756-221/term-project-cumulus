package proj756

import scala.concurrent.duration._

import io.gatling.core.Predef._
import io.gatling.http.Predef._

object Utility {
  /*
    Utility to get an Int from an environment variable.
    Return defInt if the environment var does not exist
    or cannot be converted to a string.
  */
  def envVarToInt(ev: String, defInt: Int): Int = {
    try {
      sys.env(ev).toInt
    } catch {
      case e: Exception => defInt
    }
  }

  /*
    Utility to get an environment variable.
    Return defStr if the environment var does not exist.
  */
  def envVar(ev: String, defStr: String): String = {
    sys.env.getOrElse(ev, defStr)
  }
}

object RBook {

  val feeder = csv("books.csv").eager.random

  val rbook = forever("i") {
    feed(feeder)
    .exec(http("RBook ${i}")
      .get("/api/v1/book/${UUID}"))
      .pause(1)
  }

}

object RUser {

  val feeder = csv("users.csv").eager.circular

  val ruser = forever("i") {
    feed(feeder)
    .exec(http("RUser ${i}")
      .get("/api/v1/user/${UUID}"))
    .pause(1)
  }
}

object RCheckout {

  val feeder = csv("checkout.csv").eager.circular

  val rreturn = forever("i") {
    feed(feeder)
    .exec(http("RCheckout ${i}")
      .put("/api/v1/checkout/return/${UUID}"))
    .pause(1)
  }
}

object checkoutCoverage {
  val feeder = csv("checkout.csv").eager.circular
  val rcheckout = forever("i") {
    feed(feeder)

    .exec(http("lend book")
      .put("/api/v1/checkout/lend/${UUID}")
      .header("Content-Type", "application/json")
      .body(StringBody(string = """
        "author": "${author}",
        "booktitle": "${title}"}
      """))
      .check(status.is(200)))
    .pause(1)
    .exec(http("return book")
      .put("/api/v1/checkout/return/${UUID}")
      .header("Content-Type", "application/json")
      .check(status.is(200)))
    .pause(1)

  }
}

/*
  After one S1 read, pause a random time between 1 and 60 s
*/
object RUserVarying {
  val feeder = csv("users.csv").eager.circular

  val ruser = forever("i") {
    feed(feeder)
    .exec(http("RUserVarying ${i}")
      .get("/api/v1/user/${UUID}"))
    .pause(1, 60)
  }
}

/*
  After one S2 read, pause a random time between 1 and 60 s
*/

object RBookVarying {
  val feeder = csv("books.csv").eager.circular

  val rbook = forever("i") {
    feed(feeder)
    .exec(http("RBookVarying ${i}")
      .get("/api/v1/book/${UUID}"))
    .pause(1, 60)
  }
}

/*
  Failed attempt to interleave reads from User and Books tables.
  The Gatling EDSL only honours the second (Book) read,
  ignoring the first read of User. [Shrug-emoji] 
 */
object RBoth {

  val u_feeder = csv("users.csv").eager.circular
  val c_feeder = csv("checkout.csv").eager.random
  val b_feeder = csv("books.csv").eager.random

  val rboth = forever("i") {
    feed(u_feeder)
    .exec(http("RUser ${i}")
      .get("/api/v1/user/${UUID}"))
    .pause(1);

    feed(b_feeder)
    .exec(http("RBook ${i}")
      .get("/api/v1/book/${UUID}"))
      .pause(1)

    feed(c_feeder)
    .exec(http("RCheckout ${i}")
      .get("/api/v1/lend/${book_id}"))
      .pause(1)
  }

}

// Get Cluster IP from CLUSTER_IP environment variable or default to 127.0.0.1 (Minikube)
class ReadTablesSim extends Simulation {
  val httpProtocol = http
    .baseUrl("http://" + Utility.envVar("CLUSTER_IP", "127.0.0.1") + "/")
    .acceptHeader("application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    .authorizationHeader("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGJmYmMxYzAtMDc4My00ZWQ3LTlkNzgtMDhhYTRhMGNkYTAyIiwidGltZSI6MTYwNzM2NTU0NC42NzIwNTIxfQ.zL4i58j62q8mGUo5a0SQ7MHfukBUel8yl8jGT5XmBPo")
    .acceptLanguageHeader("en-US,en;q=0.5")
}

class ReadUserSim extends ReadTablesSim {
  val scnReadUser = scenario("ReadUser")
        .exec(RUser.ruser)

  setUp(
    scnReadUser.inject(constantConcurrentUsers(Utility.envVarToInt("USERS", 1)).during(10.minutes))
  ).protocols(httpProtocol)
}

class ReadMusicSim extends ReadTablesSim {
  val scnReadMusic = scenario("ReadMusic")
    .exec(RMusic.rmusic)

  setUp(
    scnReadMusic.inject(atOnceUsers(Utility.envVarToInt("USERS", 1)))
  ).protocols(httpProtocol)
}

class ReadBookSim extends ReadTablesSim {
  val scnReadBook = scenario("ReadBook")
          .exec(RBook.rbook)
    
  setUp(
    scnReadBook.inject(constantConcurrentUsers(Utility.envVarToInt("USERS", 1)).during(10.minutes))
  ).protocols(httpProtocol)
}

class CheckoutSim extends ReadTablesSim {
  val scnReturnBook = scenario("ReturnBook")
        .exec(checkoutCoverage.rcheckout)
        
  setUp(
    scnReturnBook.inject(constantConcurrentUsers(Utility.envVarToInt("USERS", 1)).during(10.minutes))
  ).protocols(httpProtocol)
}

/*
  Read both services concurrently at varying rates.
  Ramp up new users one / 10 s until requested USERS
  is reached for each service.
*/
class ReadBothVaryingSim extends ReadTablesSim {

  val scnReadBV = scenario("ReadBookVarying")
    .exec(RBookVarying.rbook)

  val scnReadUV = scenario("ReadUserVarying")
    .exec(RUserVarying.ruser)

  val users = Utility.envVarToInt("USERS", 10)

  setUp(
    // Add one user per 10 s up to specified value
    scnReadBV.inject(rampConcurrentUsers(1).to(users).during(10*users)),
    scnReadUV.inject(rampConcurrentUsers(1).to(users).during(10*users))
  ).protocols(httpProtocol)
}

