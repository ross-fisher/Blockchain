(ns blockchain.core
  (:require [reagent.core :as r]
            [reagent.dom :as rdom]
            [goog.string :refer [format]]
            [ajax.core :refer [GET POST]]
            [cljs.core.async :refer [go go-loop timeout <! >!]]
            ))

(def state (r/atom {:id nil
                    :coins 0
                    :transactions []}))

(defn update-account
    []
    (POST "/account_info" {:params (select-keys @state [:id])
                           :format :json
                           :response-format :json
                           :handler (fn [res]
                                        (js/console.log res)
                                        (swap! state assoc :coins (:coins res)
                                                           :transactions (:transactions res))
                                        )
                           :error-handler (fn [res]
                                              (js/alert (format "Error: %s" res)))
                           :keywords? true}))


(go-loop []
   (<! (timeout 5000))
   (update-account)
   (recur))



(defn form []
 (let [temp (r/atom {:id "Account ID"})]
     (fn []
         [:div.pa2.ba.b--white.w-25.mt4
            [:div "View User Information"]
            [:form.flex.flex-column
             {:on-submit
              (fn [e]
                (.preventDefault e)
                (swap! state merge @temp)
                (reset! temp @state)
                )}
             [:input {:type :text :name :id
                      :value (:id @temp)
                      :on-change
                      (fn [e]
                        (swap! temp assoc :id
                        (-> e .-target .-value)))}]
             [:input.mt2 {:type :submit
                          :value "Select User"}]]])))


(defn transactions []
    (fn []
        [:div "Transactions"]
        [:ul
         (for [[i m] (map-indexed vector (:transactions @state))]
            ^{:key i} [:li (format "Recipient: %s. Sender: %s" (:recipient m) (:sender m))])]))

(defn account-info []
    (fn []
        [:div (format "You have %s coins" (:coins @state))]))


(defn page []
  [:<>
      [account-info]
      [form]
      [transactions]])


(defn start! []
  (rdom/render [page] (js/document.getElementById "app")))

(defn ^:export
   main []
  (start!))
