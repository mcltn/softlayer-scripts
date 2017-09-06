package main

import (
	"fmt"
	//"strings"
	//"log"

	"github.com/softlayer/softlayer-go/datatypes"
	"github.com/softlayer/softlayer-go/services"
	"github.com/softlayer/softlayer-go/session"
	"github.com/softlayer/softlayer-go/sl"
)

func getVirtualMachines() {
	sess := session.New()

	//service := services.GetVirtualGuestService(sess)
	service := services.GetAccountService(sess)

	vms, err := service.GetVirtualGuests()
	if err != nil {
		fmt.Printf("error... %s\n", err)
	} else {
		fmt.Println("VMs:")
	}

	for _, vm := range vms {
		fmt.Printf("\t[%d]%s.%s\n", *vm.Id, *vm.Hostname, *vm.Domain)
	}
}

type Billing_Order_Quote struct {
	Session *session.Session
	Options sl.Options
}

func GetBillingOrderQuoteService(sess *session.Session) Billing_Order_Quote {
	return Billing_Order_Quote{Session: sess}
}

func (r Billing_Order_Quote) Id(id int) Billing_Order_Quote {
	r.Options.Id = &id
	return r
}

func (r Billing_Order_Quote) GetRecalculatedOrderContainer() (resp datatypes.Container_Product_Order, err error) {
	err = r.Session.DoRequest("SoftLayer_Billing_Order_Quote", "getRecalculatedOrderContainer", nil, &r.Options, &resp)
	return
}

func getQuote() {
	sess := session.New()
	service := GetBillingOrderQuoteService(sess)
	//quote_container, err := service.GetRecalculatedOrderContainer(&message, &ignoreDiscountsFlag)
	quote_id := 2196017
	q, err := service.Id(quote_id).GetRecalculatedOrderContainer()
	//fmt.Printf("Resp: %s")
	if err != nil {
		fmt.Printf("error... %s\n", err)
	} else {
		fmt.Printf("Quote: %d", *q.BillingOrderItemId)
	}
}

func main() {
	//getVirtualMachines()
	getQuote()
}
