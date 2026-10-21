package cache

import (
	"testing"
	"testing/synctest"
	"time"
)

func TestExpiry(t *testing.T) {
	synctest.Test(t, func(t *testing.T) { // a "bubble" with a fake clock
		c := New()
		c.Set("token", "abc", time.Hour)

		synctest.Sleep(59 * time.Minute) // instant: the fake clock jumps
		if _, ok := c.Get("token"); !ok {
			t.Fatal("expired too early")
		}
		synctest.Sleep(2 * time.Minute) // passes the TTL; AfterFunc has run
		if _, ok := c.Get("token"); ok {
			t.Fatal("not expired after the TTL")
		}
		t.Log("fake time now:", time.Now().Format("15:04"))
	})
}
