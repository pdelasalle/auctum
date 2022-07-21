from django.db import models

class transactions(models.Model):
    
    id = models.TextField(db_column='tx_id', null=False,primary_key=True) 
    
    sender = models.TextField(db_column='sender', blank=True, null=True) 
    pair = models.TextField(db_column='pair', blank=True, null=True) 
    side = models.TextField(db_column='side', blank=True, null=True)     
    qty_side = models.FloatField(db_column='qty_side', blank=True, null=True) 
    qty_other_side = models.FloatField(db_column='qty_other_side', blank=True, null=True)     
    token_send = models.TextField(db_column='token_send', blank=True, null=True)     
    token_receive = models.TextField(db_column='token_receive', blank=True, null=True)     
    qty_send = models.FloatField(db_column='qty_send', blank=True, null=True)     
    qty_receive = models.FloatField(db_column='qty_receive', blank=True, null=True)     
    price = models.FloatField(db_column='price', blank=True, null=True)     
    timestamp =  models.FloatField(db_column='timestamp', blank=True, null=True) 
    matching_id =  models.TextField(db_column='matching_id', blank=True, null=True) 
    matched =  models.TextField(db_column='matched', blank=True, null=True) 

    def __int__(self):
        return self.table_id
	
    class Meta:
        db_table = 'transactions'
        
class pairs(models.Model):
    
    id = models.TextField(db_column='pair_id', null=False,primary_key=True) 
    
    ccy1 = models.TextField(db_column='ccy1', blank=True, null=True) 
    ccy2 = models.TextField(db_column='ccy2', blank=True, null=True) 

    def __int__(self):
        return self.table_id
	
    class Meta:
        db_table = 'pairs'
        
        
class balances(models.Model):
    
    id = models.TextField(db_column='sender', null=False,primary_key=True) 
    
    eth = models.FloatField(db_column='eth', blank=True, null=True) 
    crv = models.FloatField(db_column='crv', blank=True, null=True) 
    usdc = models.FloatField(db_column='usdc', blank=True, null=True) 

    def __int__(self):
        return self.table_id
	
    class Meta:
        db_table = 'balances'